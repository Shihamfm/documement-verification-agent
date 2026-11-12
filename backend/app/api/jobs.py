from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.job import Job
from backend.app.schemas.job import JobResponse
from backend.app.api.dependencies import get_current_user
from backend.app.services.telemetry import telemetry_hub

router = APIRouter(prefix="/api/jobs", tags=["Jobs & Pipeline"])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves full status, duration, and granular stage logs for a processing job."""
    stmt = (
        select(Job)
        .options(selectinload(Job.stages))
        .where(Job.id == job_id)
    )
    job = (await db.execute(stmt)).scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to view this job."
        )

    return job


@router.get("/{job_id}/events")
async def stream_job_events(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Server-Sent Events (SSE) streaming endpoint for real-time pipeline visualization."""
    stmt = (
        select(Job)
        .options(selectinload(Job.stages))
        .where(Job.id == job_id)
    )
    job = (await db.execute(stmt)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    # Calculate initial progress
    completed_stages = sum(1 for s in job.stages if s.status == "completed")
    total_stages = max(len(job.stages), 1)
    progress_pct = int((completed_stages / total_stages) * 100) if job.status != "completed" else 100

    initial_state = {
        "job_id": job.id,
        "stage_name": job.current_stage,
        "status": job.status,
        "progress_percentage": progress_pct,
        "error_message": job.error_message,
        "stages": [
            {
                "stage_name": s.stage_name,
                "status": s.status,
                "duration_seconds": s.duration_seconds
            }
            for s in job.stages
        ]
    }

    return StreamingResponse(
        telemetry_hub.sse_event_generator(job_id=job.id, initial_state=initial_state),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
