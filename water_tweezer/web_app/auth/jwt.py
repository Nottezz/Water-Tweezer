from datetime import UTC, datetime, timedelta

import jwt


def create_jwt_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(UTC) + timedelta(minutes=60),
    }
    return jwt.encode(payload)
