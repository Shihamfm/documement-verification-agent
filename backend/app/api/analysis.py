from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.entity import PrescribedEntity
from backend.app.models.summary import DocumentSummary, CriticalPoint
from backend.app.schemas.analysis import (
    DocumentAnalysisResponse,
    DocumentSummaryResponse,
    CriticalPointResponse
)
from backend.app.schemas.entity import PrescribedEntityResponse, VerificationResultResponse
from backend.app.api.dependencies import get_current_user
from backend.app.services.parser import DocumentParser

router = APIRouter(prefix="/api/analysis", tags=["Analysis & Verification"])


@router.get("/{document_id}", response_model=DocumentAnalysisResponse)
async def get_document_analysis(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves full clinical analysis bundle for a primary document:

    executive summary, ranked critical points, structured medication entities,
    formulary verification results, grounded citations, and original document text.
    """
    # 1. Fetch Primary Document
    stmt_doc = select(Document).where(Document.id == document_id)
    doc = (await db.execute(stmt_doc)).scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    if doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to view this analysis."
        )

    # 2. Fetch Summary
    stmt_sum = select(DocumentSummary).where(DocumentSummary.document_id == document_id)
    summary_obj = (await db.execute(stmt_sum)).scalar_one_or_none()
    summary_resp = (
        DocumentSummaryResponse(
            id=summary_obj.id,
            executive_summary=summary_obj.executive_summary,
            clinical_highlights=summary_obj.clinical_highlights,
            created_at=summary_obj.created_at
        )
        if summary_obj
        else None
    )

    # 3. Fetch Critical Points
    stmt_pts = (
        select(CriticalPoint)
        .where(CriticalPoint.document_id == document_id)
        .order_by(CriticalPoint.rank_order.asc())
    )
    points_objs = (await db.execute(stmt_pts)).scalars().all()
    critical_points_resp = [
        CriticalPointResponse(
            id=p.id,
            point_text=p.point_text,
            category=p.category,
            severity=p.severity,
            source_quote=p.source_quote,
            rank_order=p.rank_order
        )
        for p in points_objs
    ]

    # 4. Fetch Prescribed Entities with Verification Results
    stmt_ents = (
        select(PrescribedEntity)
        .options(selectinload(PrescribedEntity.verification_result))
        .where(PrescribedEntity.document_id == document_id)
    )
    entity_objs = (await db.execute(stmt_ents)).scalars().all()

    entities_resp = []
    supported_cnt = 0
    contradicted_cnt = 0
    unsupported_cnt = 0

    for ent in entity_objs:
        vr = ent.verification_result
        vr_resp = (
            VerificationResultResponse(
                id=vr.id,
                status=vr.status,
                explanation=vr.explanation,
                parameter_matches=vr.parameter_matches,
                citation_section=vr.citation_section,
                citation_monograph=vr.citation_monograph,
                citation_passage=vr.citation_passage,
                created_at=vr.created_at
            )
            if vr
            else None
        )

        if vr:
            if vr.status == "Supported":
                supported_cnt += 1
            elif vr.status == "Contradicted":
                contradicted_cnt += 1
            elif vr.status == "Unsupported":
                unsupported_cnt += 1

        entities_resp.append(
            PrescribedEntityResponse(
                id=ent.id,
                medication_name=ent.medication_name,
                dose=ent.dose,
                unit=ent.unit,
                route=ent.route,
                frequency=ent.frequency,
                duration=ent.duration,
                indication=ent.indication,
                source_section=ent.source_section,
                raw_attributes=ent.raw_attributes,
                verification=vr_resp
            )
        )

    patient_info = doc.doc_metadata.get("patient_info", DocumentParser.extract_patient_info(doc.raw_text))
    sections = DocumentParser.extract_clinical_sections(doc.raw_text)

    return DocumentAnalysisResponse(
        document_id=doc.id,
        filename=doc.filename,
        patient_info=patient_info,
        summary=summary_resp,
        critical_points=critical_points_resp,
        prescribed_entities=entities_resp,
        raw_text=doc.raw_text,
        sections=sections,
        total_medications=len(entities_resp),
        supported_count=supported_cnt,
        contradicted_count=contradicted_cnt,
        unsupported_count=unsupported_cnt
    )
