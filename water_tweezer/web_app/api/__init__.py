from fastapi import APIRouter

from .settings import router as settings_router
from .statistics import router as statistics_router

router = APIRouter(prefix="/api")
router.include_router(settings_router)
router.include_router(statistics_router)
