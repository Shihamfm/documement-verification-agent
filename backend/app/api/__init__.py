from backend.app.api.auth import router as auth_router
from backend.app.api.documents import router as documents_router
from backend.app.api.jobs import router as jobs_router
from backend.app.api.analysis import router as analysis_router

__all__ = [
    "auth_router",
    "documents_router",
    "jobs_router",
    "analysis_router"
]
