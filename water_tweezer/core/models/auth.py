from pydantic import BaseModel


class AuthRequest(BaseModel):
    init_data: str


class AuthResponse(BaseModel):
    access_token: str
    user: str


class CurrentUser(BaseModel):
    id: int
