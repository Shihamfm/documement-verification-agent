# Document Verification System — Requirements Analysis Specification

**Project**: Institutional Clinical Document Verification Agent  
**Domain**: Inpatient Pharmacy & Discharge Medication Verification  
**Evaluation Standard**: Lead AI/ML & Full-Stack Engineer Technical Assessment  
**Document Revision**: 1.0.0  
**Date**: November 2026  

---

## 1. Project Overview

The **Document Verification System** is an end-to-end clinical workflow application engineered to ingest hospital discharge summaries (primary documents), extract clinical narratives, summarize clinical discharge details, surface patient safety-critical action items, extract structured medication regimens, and verify each prescribed entity against an authoritative institutional formulary digest (reference document) using Retrieval-Augmented Generation (RAG) and targeted parameter validation.

The system ensures that discharge prescriptions comply with institutional prescribing guidelines, identifying dosage mismatches, timing deviations, unapproved durations, and unlisted medications before patient discharge.

---

## 2. Problem Statement

Discharge medication errors represent one of the most common and preventable causes of post-discharge adverse drug events (ADEs), readmissions, and patient harm. In hospital settings:
1. Inpatient physicians prescribe complex regimens under time pressure, occasionally departing from institutional formulary standards regarding standard initial dosages, chronopharmacological administration timing (e.g., bedtime vs. morning), and therapy duration limits.
2. Discharge summaries interweave clinical history, lab progress, counseling notes, and prescriptions across narrative blocks, making manual cross-referencing against formulary monographs labor-intensive and error-prone.
3. Patients frequently miss critical post-discharge instructions (such as red-flag symptoms requiring emergency evaluation, follow-up lab timing, or abrupt cessation risks) when buried in dense narrative documents.

Automated, asynchronous, grounded verification with precise citations to the institutional formulary allows clinicians, clinical pharmacists, and review personnel to immediately isolate contradictions and safeguard patient transitions of care.

---

## 3. Project Objectives

- **Asynchronous Processing Pipeline**: Provide a non-blocking ingestion and verification architecture with granular, observable stages (`parsed` → `chunked` → `embedded` → `summarized` → `key_points_extracted` → `entities_extracted` → `verified` → `done`).
- **Real-Time Client Telemetry**: Stream stage transitions, execution metrics, and completion notifications to the client interface via Server-Sent Events (SSE) and WebSockets with resilient reconnection and refresh survival.
- **Precision Information Extraction**: Reliably extract structured prescription records (drug name, dose, unit, route, frequency, duration, indication, source location) with zero hallucination.
- **RAG-Grounded Formulary Verification**: Implement domain-aware chunking of institutional monographs, dense semantic embeddings, and parameter-level verification comparing claims against formulary ground truth to assign one of three explicit states:
  - **Supported**: Drug exists in formulary and all parameters (dose, frequency, route, timing, duration) comply.
  - **Contradicted**: Drug exists in formulary, but one or more prescribing parameters conflict with institutional monographs (wrong dose, timing, duration, etc.).
  - **Unsupported**: Drug does not exist in the institutional formulary digest.
- **Citation Traceability & Deep Linking**: Ground every flagged contradiction in verifiable citations citing specific sections, monographs, and passage text, enabling one-click reference previews and deep linking into the formulary text.
- **Patient Critical Point Prioritization**: Surface ranked patient-centric warnings (critical timing, duration bounds, monitoring appointments, urgent side effects) faithfully extracted without inventing unsupported clinical claims.
- **Enterprise-Ready Full-Stack Security**: Implement secure multi-tenant data isolation, JWT authentication, atomic database transactions for document uploads, content-hash deduplication, and containerized deployment.

---

## 4. User Roles and Permissions

| Role | Permissions | Access Scope |
| :--- | :--- | :--- |
| **Clinical Pharmacist / Reviewer** (Authenticated User) | Ingest primary discharge summaries, select reference formularies, monitor verification progress in real time, inspect extracted entities, audit flagged issues, deep-link reference citations, download reports. | Strict tenant boundary: can view and manage only documents and verification jobs belonging to their own user account. |
| **System / Pipeline Engine** | Execute background parsing, embedding generation, vector search, LLM orchestration, and state persistence. | Internal asynchronous worker permissions with transactional database rollback. |

---

## 5. Input and Output Specifications

### 5.1 System Inputs
- **Primary Document**: Inpatient Discharge Summary in DOCX or PDF format (e.g., `primary_document_medical.docx`). Contains narrative hospital course, discharge diagnoses, medication table, patient counseling warnings, and follow-up schedules.
- **Reference Document**: Institutional Formulary Digest in DOCX or PDF format (e.g., `reference_document_medical.docx`). Contains structured monographs with therapeutic classes, standard adult doses, maximum doses, administration timing, contraindications, drug interactions, monitoring requirements, and prescribing notes.
- **Authentication Credentials**: User credentials (email/username and password) via JSON payload.

### 5.2 System Outputs
- **Job Status Stream**: Real-time event stream (`event: stage_update`) emitting stage name, status (`pending`, `in_progress`, `completed`, `failed`), progress percentage, duration, and timestamp.
- **Executive Discharge Summary**: Faithful clinical overview synthesizing admission rationale, hospital course, hemodynamic stabilization, and discharge readiness.
- **Prioritized Critical Points**: List of patient safety items categorized by type (`timing_critical`, `duration_limit`, `urgent_adverse_effect`, `abrupt_discontinuation_warning`, `follow_up_lab`), ranked by severity (High, Medium, Low), with primary text excerpts.
- **Structured Medication Entities**: JSON collection of extracted prescriptions:
  - `medication_name`: string (e.g., "Pravoxil")
  - `dose`: string / float (e.g., "20 mg")
  - `route`: string (e.g., "PO")
  - `frequency`: string (e.g., "every morning")
  - `duration`: string (e.g., "Continue indefinitely")
  - `indication`: string (e.g., "Hyperlipidemia")
  - `source_section`: string (e.g., "Section 4. Discharge Medications")
- **Formulary Verification Results**:
  - `status`: `"Supported"` | `"Contradicted"` | `"Unsupported"`
  - `parameter_match`: Breakdown of dose match, frequency match, duration match, timing match, indication match.
  - `explanation`: Detailed explanation of clinical concordance or contradiction.
  - `citation`: Grounded reference passage, section number/title, monograph name, page number.

---

## 6. Functional Requirements

### FR-01: Authentication & Authorization
- FR-01.1: System shall authenticate users via email and password using salted bcrypt password hashes.
- FR-01.2: System shall issue cryptographically signed JWT access tokens for protected API routes.
- FR-01.3: System shall enforce row-level tenant isolation: users cannot view, query, or mutate documents or verification jobs belonging to other users.

### FR-02: Document Ingestion & Storage
- FR-02.1: System shall accept DOCX and PDF document uploads for primary documents and reference documents.
- FR-02.2: Primary document upload shall return an immediate HTTP 202 Accepted response containing a unique `job_id`. The upload endpoint shall never block on pipeline processing.
- FR-02.3: System shall execute document creation and job initialization within an atomic database transaction. If any creation step fails, database state rolls back cleanly.
- FR-02.4: System shall compute a SHA-256 content hash of uploaded files. If a duplicate primary document is uploaded by the same user within 5 minutes (configurable), the system returns the existing job ID rather than spawning redundant pipelines.

### FR-03: Asynchronous Pipeline & Granular Telemetry
- FR-03.1: Pipeline must execute through seven distinct, named stages:
  1. `parsed`: Document text, sections, and metadata extracted.
  2. `chunked`: Reference document partitioned into monograph sections.
  3. `embedded`: Monograph chunks vector-embedded.
  4. `summarized`: LLM generates faithful clinical discharge summary.
  5. `key_points_extracted`: Critical patient-facing action items extracted and ranked.
  6. `entities_extracted`: Structured medication prescriptions extracted as valid JSON.
  7. `verified`: Prescribed parameters verified against retrieved formulary monographs.
- FR-03.2: Pipeline shall expose a Server-Sent Events (SSE) endpoint and WebSocket endpoint streaming live stage transitions with timestamps.
- FR-03.3: Client shall be able to refresh mid-processing without loss of state or pipeline tracking.
- FR-03.4: Per-stage exception isolation: any failure sets job state to `failed` with descriptive diagnostic error logs, preventing hung processes.

### FR-04: Knowledge Chunking & RAG Retrieval
- FR-04.1: Reference documents shall be chunked using a monograph-aware strategy that preserves drug name, therapeutic category, standard dose, administration rules, contraindications, and prescribing notes.
- FR-04.2: Chunks shall be stored in PostgreSQL with pgvector (vector similarity using cosine distance) with metadata indexing.
- FR-04.3: Targeted retrieval shall retrieve the top relevant monograph chunks for each extracted medication entity based on semantic similarity and drug name keyword grounding.

### FR-05: Clinical Entity Extraction & Verification
- FR-05.1: System shall extract all prescribed medications with dose, unit, route, frequency, duration, and indication into a strict Pydantic model.
- FR-05.2: Verification engine shall compare prescribed parameters (dose amount, frequency, administration timing, duration) against formulary monograph parameters.
- FR-05.3: Verification must categorize each entity into Supported, Contradicted, or Unsupported:
  - Supported: Parameters within formulary guidelines.
  - Contradicted: Clear divergence from formulary monograph (e.g., Pravoxil morning vs. bedtime; Etrazolam 8 weeks vs. 4 weeks limit; Cordizem-XR 100 mg initial vs. 50 mg standard).
  - Unsupported: Drug absent from formulary digest (e.g., Pranixol).
- FR-05.4: Hallucination Safeguard: Citations must reference exact text passages from the formulary document. If ungrounded or absent, the system explicitly reports no supporting passage found.

### FR-06: Interactive Presentation & Deep Linking
- FR-06.1: Dual-pane UI: primary document viewer on the left, tabbed verification workbench on the right.
- FR-06.2: Interactive citation cards: clicking an issue expands the citation details, highlighting the excerpt.
- FR-06.3: Deep link into reference document: clicking "View in Reference" navigates the user to the exact passage in the reference formulary viewer.
- FR-06.4: Optimistic UI updates, responsive design, comprehensive loading, empty, and error boundary states.

---

## 7. Non-Functional Requirements

- **Performance**: Document ingestion endpoint response time < 250ms; pipeline completion time < 20 seconds for standard discharge summaries.
- **Reliability & Idempotency**: Atomic transactions prevent partial records; duplicate submission suppression avoids redundant computational load.
- **Portability**: Deployable via single `docker-compose up --build` command across Windows, macOS, and Linux.
- **Observability**: Structured JSON logging across all pipeline stages with correlation IDs (`job_id`, `document_id`, `user_id`).
- **Offline / Resilient Execution**: Hybrid LLM provider architecture supporting Gemini API, OpenAI API, Ollama, and an integrated deterministic verification engine guaranteeing 100% test reproducibility even without active cloud API keys.

---

## 8. Evaluation Criteria Mapping

| Criterion | Target Implementation in Repository |
| :--- | :--- |
| **50% AI / GenAI & RAG** | Monograph-aware RAG chunker, dense vector embeddings with cosine similarity, targeted retrieval, structured JSON schema extraction, parameter-level verification engine, hallucination control with grounded citations, prioritized critical-point ranking. |
| **50% Full-Stack Engineering** | Asynchronous FastAPI background pipeline, non-blocking upload endpoint, real-time SSE telemetry, PostgreSQL with pgvector schema & versioned migrations, React + TypeScript + Tailwind UI, optimistic UI patterns, atomic upload transactions, multi-tenant user isolation, end-to-end test suite, Docker containerization. |
| **Extra Credit Features** | 1) Deep-linking citations directly into the rendered reference document. 2) SHA-256 duplicate upload detection with configurable 5-minute deduplication window. |
