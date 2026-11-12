import sys
from pathlib import Path
for _p in Path(__file__).resolve().parents:
    if (_p / 'backend').is_dir() and (_p / 'pyproject.toml').is_file():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break

import time
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.session import AsyncSessionLocal
from backend.app.models.job import Job, JobStage
from backend.app.models.document import Document
from backend.app.models.rag import FormularyChunk
from backend.app.models.entity import PrescribedEntity, VerificationResult
from backend.app.models.summary import DocumentSummary, CriticalPoint
from backend.app.services.parser import DocumentParser
from backend.app.services.chunker import MonographChunker
from backend.app.services.rag import RAGService
from backend.app.services.llm import ClinicalLLMService
from backend.app.services.verifier import ClinicalVerifier
from backend.app.services.telemetry import telemetry_hub
from backend.app.core.logger import logger


PIPELINE_STAGES = [
    ("parsed", "Document Ingestion & Section Parsing", 10),
    ("chunked", "Monograph Partitioning & Hierarchy", 25),
    ("embedded", "Vector Embedding Generation", 40),
    ("summarized", "Executive Discharge Summarization", 55),
    ("key_points_extracted", "Patient Safety Critical Point Extraction", 70),
    ("entities_extracted", "Structured Prescription Entity Extraction", 85),
    ("verified", "Formulary RAG Retrieval & Verification", 95),
]


class AsyncPipelineEngine:
    """Executes asynchronous document verification through granular observable stages."""

    @classmethod
    async def run_pipeline(cls, job_id: str, session_factory=None) -> None:
        """Entry point executed in background task."""
        maker = session_factory or AsyncSessionLocal
        logger.info(f"Starting asynchronous pipeline for job_id={job_id}")

        async with maker() as db:
            job = await db.get(Job, job_id)
            if not job:
                logger.error(f"Job {job_id} not found in database.")
                return

            primary_doc = await db.get(Document, job.primary_document_id)
            ref_doc = await db.get(Document, job.reference_document_id)
            if not primary_doc or not ref_doc:
                await cls._fail_job(db, job, "Required primary or reference document record is missing.")
                return

            job.status = "processing"
            await db.commit()

        context: Dict[str, Any] = {
            "primary_raw_text": primary_doc.raw_text,
            "primary_file_type": primary_doc.file_type,
            "ref_raw_text": ref_doc.raw_text,
            "ref_file_type": ref_doc.file_type,
            "parsed_primary": None,
            "monograph_chunks": [],
            "summary": None,
            "critical_points": [],
            "prescribed_entities": [],
            "verification_results": []
        }

        try:
            # 1. parsed
            await cls._execute_stage(
                job_id, "parsed", 15,
                lambda: cls._stage_parsed(primary_doc, context, maker),
                maker
            )

            # 2. chunked
            await cls._execute_stage(
                job_id, "chunked", 30,
                lambda: cls._stage_chunked(ref_doc, context),
                maker
            )

            # 3. embedded
            await cls._execute_stage(
                job_id, "embedded", 45,
                lambda: cls._stage_embedded(ref_doc, context, maker),
                maker
            )

            # 4. summarized
            await cls._execute_stage(
                job_id, "summarized", 60,
                lambda: cls._stage_summarized(primary_doc, context, maker),
                maker
            )

            # 5. key_points_extracted
            await cls._execute_stage(
                job_id, "key_points_extracted", 75,
                lambda: cls._stage_key_points(primary_doc, context, maker),
                maker
            )

            # 6. entities_extracted
            await cls._execute_stage(
                job_id, "entities_extracted", 88,
                lambda: cls._stage_entities(primary_doc, context, maker),
                maker
            )

            # 7. verified
            await cls._execute_stage(
                job_id, "verified", 98,
                lambda: cls._stage_verified(primary_doc, ref_doc, context, maker),
                maker
            )

            # Terminal Completed State
            async with maker() as db:
                job_obj = await db.get(Job, job_id)
                if job_obj:
                    job_obj.status = "completed"
                    job_obj.current_stage = "done"
                    job_obj.completed_at = datetime.now(timezone.utc)
                    await db.commit()

            await telemetry_hub.emit_event(
                job_id=job_id,
                stage_name="done",
                status="completed",
                progress=100,
                metadata={"total_entities": len(context.get("prescribed_entities", []))}
            )
            logger.info(f"Pipeline successfully completed for job_id={job_id}")

        except Exception as e:
            logger.exception(f"Pipeline failed at stage for job {job_id}: {e}")
            async with maker() as db:
                job_obj = await db.get(Job, job_id)
                if job_obj:
                    await cls._fail_job(db, job_obj, str(e))

    @classmethod
    async def _execute_stage(cls, job_id: str, stage_name: str, progress: int, stage_fn, maker) -> None:
        start_time = time.time()
        start_dt = datetime.now(timezone.utc)

        async with maker() as db:
            stmt = select(JobStage).where(JobStage.job_id == job_id, JobStage.stage_name == stage_name)
            res = await db.execute(stmt)
            stage_rec = res.scalar_one_or_none()
            if stage_rec:
                stage_rec.status = "in_progress"
                stage_rec.started_at = start_dt
                await db.commit()

            job_rec = await db.get(Job, job_id)
            if job_rec:
                job_rec.current_stage = stage_name
                await db.commit()

        await telemetry_hub.emit_event(
            job_id=job_id,
            stage_name=stage_name,
            status="in_progress",
            progress=progress
        )

        res = stage_fn()
        if asyncio.iscoroutine(res):
            stage_meta = await res
        else:
            stage_meta = res

        duration = round(time.time() - start_time, 3)
        end_dt = datetime.now(timezone.utc)

        async with maker() as db:
            stmt = select(JobStage).where(JobStage.job_id == job_id, JobStage.stage_name == stage_name)
            res = await db.execute(stmt)
            stage_rec = res.scalar_one_or_none()
            if stage_rec:
                stage_rec.status = "completed"
                stage_rec.completed_at = end_dt
                stage_rec.duration_seconds = duration
                stage_rec.stage_metadata = stage_meta or {}
                await db.commit()

        await telemetry_hub.emit_event(
            job_id=job_id,
            stage_name=stage_name,
            status="completed",
            progress=progress,
            metadata={"duration_seconds": duration, **(stage_meta or {})}
        )

    # -------------------------------------------------------------
    # Stage Handlers
    # -------------------------------------------------------------
    @classmethod
    async def _stage_parsed(cls, primary_doc: Document, ctx: Dict[str, Any], maker) -> Dict[str, Any]:
        sections = DocumentParser.extract_clinical_sections(primary_doc.raw_text)
        patient_info = DocumentParser.extract_patient_info(primary_doc.raw_text)

        ctx["parsed_primary"] = {
            "sections": sections,
            "patient_info": patient_info
        }

        async with maker() as db:
            doc = await db.get(Document, primary_doc.id)
            if doc:
                meta = dict(doc.doc_metadata or {})
                meta["sections"] = list(sections.keys())
                meta["patient_info"] = patient_info
                doc.doc_metadata = meta
                await db.commit()

        return {"sections_count": len(sections), "patient": patient_info.get("patient_name")}

    @classmethod
    async def _stage_chunked(cls, ref_doc: Document, ctx: Dict[str, Any]) -> Dict[str, Any]:
        chunks = MonographChunker.chunk_reference_document(ref_doc.raw_text)
        ctx["monograph_chunks"] = chunks
        return {"chunks_count": len(chunks)}

    @classmethod
    async def _stage_embedded(cls, ref_doc: Document, ctx: Dict[str, Any], maker) -> Dict[str, Any]:
        chunks = ctx["monograph_chunks"]
        async with maker() as db:
            stmt = select(FormularyChunk).where(FormularyChunk.document_id == ref_doc.id)
            existing = (await db.execute(stmt)).scalars().all()
            if not existing:
                await RAGService.index_reference_chunks(db, ref_doc.id, chunks)
                await db.commit()
        return {"indexed_chunks": len(chunks)}

    @classmethod
    async def _stage_summarized(cls, primary_doc: Document, ctx: Dict[str, Any], maker) -> Dict[str, Any]:
        parsed = ctx["parsed_primary"] or {}
        sections = parsed.get("sections", {})
        patient_info = parsed.get("patient_info", {})

        summary_data = await ClinicalLLMService.generate_summary(
            primary_text=primary_doc.raw_text,
            sections=sections,
            patient_info=patient_info
        )
        ctx["summary"] = summary_data

        async with maker() as db:
            stmt = select(DocumentSummary).where(DocumentSummary.document_id == primary_doc.id)
            existing = (await db.execute(stmt)).scalar_one_or_none()
            if not existing:
                summary_obj = DocumentSummary(
                    document_id=primary_doc.id,
                    executive_summary=summary_data["executive_summary"],
                    clinical_highlights=summary_data["clinical_highlights"]
                )
                db.add(summary_obj)
                await db.commit()

        return {"summary_length": len(summary_data["executive_summary"])}

    @classmethod
    async def _stage_key_points(cls, primary_doc: Document, ctx: Dict[str, Any], maker) -> Dict[str, Any]:
        parsed = ctx["parsed_primary"] or {}
        sections = parsed.get("sections", {})

        points = await ClinicalLLMService.extract_critical_points(primary_doc.raw_text, sections)
        ctx["critical_points"] = points

        async with maker() as db:
            stmt = select(CriticalPoint).where(CriticalPoint.document_id == primary_doc.id)
            existing = (await db.execute(stmt)).scalars().all()
            if not existing:
                for pt in points:
                    pt_obj = CriticalPoint(
                        document_id=primary_doc.id,
                        point_text=pt["point_text"],
                        category=pt["category"],
                        severity=pt["severity"],
                        source_quote=pt["source_quote"],
                        rank_order=pt["rank_order"]
                    )
                    db.add(pt_obj)
                await db.commit()

        return {"points_count": len(points)}

    @classmethod
    async def _stage_entities(cls, primary_doc: Document, ctx: Dict[str, Any], maker) -> Dict[str, Any]:
        raw_entities = await ClinicalLLMService.extract_medication_entities(primary_doc.raw_text, [])
        ctx["prescribed_entities"] = raw_entities

        async with maker() as db:
            stmt = select(PrescribedEntity).where(PrescribedEntity.document_id == primary_doc.id)
            existing = (await db.execute(stmt)).scalars().all()
            if not existing:
                for ent in raw_entities:
                    ent_obj = PrescribedEntity(
                        document_id=primary_doc.id,
                        medication_name=ent["medication_name"],
                        dose=ent["dose"],
                        unit=ent["unit"],
                        route=ent["route"],
                        frequency=ent["frequency"],
                        duration=ent["duration"],
                        indication=ent["indication"],
                        source_section=ent["source_section"],
                        raw_attributes=ent["raw_attributes"]
                    )
                    db.add(ent_obj)
                await db.commit()

        return {"entities_count": len(raw_entities)}

    @classmethod
    async def _stage_verified(cls, primary_doc: Document, ref_doc: Document, ctx: Dict[str, Any], maker) -> Dict[str, Any]:
        verified_results = []
        async with maker() as db:
            entities_query = select(PrescribedEntity).where(PrescribedEntity.document_id == primary_doc.id)
            db_entities = (await db.execute(entities_query)).scalars().all()

            for ent in db_entities:
                candidates = await RAGService.retrieve_candidates(
                    db=db,
                    document_id=ref_doc.id,
                    query=f"{ent.medication_name} {ent.dose} {ent.route} {ent.frequency}",
                    drug_name=ent.medication_name,
                    top_k=2
                )

                verification = ClinicalVerifier.verify_entity(
                    entity={
                        "medication_name": ent.medication_name,
                        "dose": ent.dose,
                        "unit": ent.unit,
                        "route": ent.route,
                        "frequency": ent.frequency,
                        "duration": ent.duration,
                        "indication": ent.indication
                    },
                    retrieved_chunks=candidates
                )

                stmt_v = select(VerificationResult).where(VerificationResult.entity_id == ent.id)
                existing_v = (await db.execute(stmt_v)).scalar_one_or_none()
                if not existing_v:
                    vr = VerificationResult(
                        entity_id=ent.id,
                        status=verification["status"],
                        explanation=verification["explanation"],
                        parameter_matches=verification["parameter_matches"],
                        citation_section=verification["citation_section"],
                        citation_monograph=verification["citation_monograph"],
                        citation_passage=verification["citation_passage"]
                    )
                    db.add(vr)

                verified_results.append({
                    "medication": ent.medication_name,
                    "status": verification["status"]
                })

            await db.commit()

        return {"verified_count": len(verified_results), "results": verified_results}

    @classmethod
    async def _fail_job(cls, db: AsyncSession, job: Job, error_msg: str) -> None:
        job.status = "failed"
        job.error_message = error_msg
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()

        await telemetry_hub.emit_event(
            job_id=job.id,
            stage_name=job.current_stage,
            status="failed",
            progress=0,
            error_message=error_msg
        )
