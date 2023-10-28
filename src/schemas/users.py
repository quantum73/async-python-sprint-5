from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from core.config import settings


class TokenOutputSchema(BaseModel):
    access_token: str
    token_type: str = settings.jwt.token_type


class UserBaseSchema(BaseModel):
    username: str


class UserInputSchema(UserBaseSchema):
    password_hash: str


class UserOutputSchema(UserBaseSchema):
    id: UUID
    created_at: datetime


class UserOutputDBSchema(UserOutputSchema):
    class Config:
        from_attributes = True
