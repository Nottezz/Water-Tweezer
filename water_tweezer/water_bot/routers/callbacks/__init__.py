__all__ = ("router",)

from aiogram import Router

from .intake import router as intake_router
from .settings import router as settings_router

router = Router(name=__name__)
router.include_router(intake_router)
router.include_router(settings_router)
