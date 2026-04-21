import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

from water_tweezer.core.config import settings
from water_tweezer.core.models.auth import CurrentUser

security = HTTPBearer()


def get_current_user(token: str = Depends(security)) -> CurrentUser:
    try:
        payload = jwt.decode(
            token.credentials,
            settings.access_token.secret_key,
            algorithms=[settings.access_token.algorithm],
        )
        return CurrentUser(id=int(payload["sub"]))

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid token"
        )
