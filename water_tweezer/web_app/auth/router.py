import json

from fastapi import APIRouter, HTTPException, status

from water_tweezer.core.config import settings
from water_tweezer.core.models.auth import AuthRequest, AuthResponse

from .jwt import create_jwt_token
from .telegram import verify_telegram_init_data

router = APIRouter(prefix="/auth", tags=["Telegram auth"])


@router.post("/verify")
def auth_verify(payload: AuthRequest) -> AuthResponse:
    try:
        data = verify_telegram_init_data(payload.init_data, settings.telegram_bot_token)

        user = data.get("user")
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No user in initData"
            )

        user_obj = json.loads(user)

        token = create_jwt_token(user_obj["id"])

        return AuthResponse(
            access_token=token,
            user=user_obj,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
