import typing as tp

from fastapi import APIRouter, Depends, status, Body
from fastapi.security import OAuth2PasswordRequestForm, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from schemas import users as users_schemas
from services import users as users_services

user_router = APIRouter()


@user_router.post(
    "/register",
    response_model=users_schemas.UserOutputDBSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    form_data: tp.Annotated[HTTPBasicCredentials, Body()],
    db: AsyncSession = Depends(get_session),
):
    new_user = await users_services.create_user(db, username=form_data.username, password=form_data.password)
    return new_user


@user_router.post("/auth", response_model=users_schemas.TokenOutputSchema)
async def auth(
    form_data: tp.Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_session),
):
    user = await users_services.authenticate_user(db, username=form_data.username, password=form_data.password)
    access_token = users_services.create_access_token(data={"sub": user.username})
    return {"access_token": access_token}
