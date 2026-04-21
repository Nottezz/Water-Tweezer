from fastapi import APIRouter, Depends
from web_app.security import get_current_user

from water_tweezer.core import crud

router = APIRouter(prefix="/settings", tags=["User settings"])


@router.get("/")
async def get_user_settings(user_id: int = Depends(get_current_user)):
    pass


@router.post("/")
async def update_user_settings(user_id: int = Depends(get_current_user)):
    pass
