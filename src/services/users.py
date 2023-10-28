import logging
import typing as tp
from datetime import timedelta, datetime

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exceptions import UnauthorizedException, BadRequestException
from core.utils import PasswordHasher
from db import get_session
from repositories.base import ModelType
from repositories.users import users_crud
from schemas import users as users_schemas

logger = logging.getLogger(__name__)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(*, data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)
    return encoded_jwt


def get_username_from_token(*, token: str) -> str:
    try:
        payload = jwt.decode(token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])
        username: str | None = payload.get("sub")
        if username is None:
            logger.error("Invalid user data from JWT token")
            raise UnauthorizedException()
    except JWTError:
        logger.error("Invalid JWT token")
        raise UnauthorizedException()
    return username


async def create_user(db: AsyncSession, *, username: str, password: str) -> ModelType:
    logger.info("Try to create user")
    user = await users_crud.get_by_username(db, username=username)
    if user:
        logger.error(f"User {username} already exists")
        raise BadRequestException(detail="User with such username already exists")

    hashed_password = PasswordHasher.get_password_hash(password=password)
    try:
        obj_in_data = {"username": username, "password_hash": hashed_password}
        user = await users_crud.create(db, obj_in=obj_in_data)
    except Exception as err:
        logger.error(err)
        raise BadRequestException(detail="Invalid data")

    logger.info("User has been created")
    return user


async def authenticate_user(db: AsyncSession, *, username: str, password: str) -> ModelType | bool:
    logger.info("Try to authenticate user")
    user = await users_crud.get_by_username(db, username=username)
    if not user:
        logger.error("User does not exist")
        raise UnauthorizedException()

    if not PasswordHasher.verify_password(plain_password=password, hashed_password=user.password_hash):
        logger.error("Incorrect password")
        raise UnauthorizedException()

    logger.info("Success authenticate user")
    return user


async def get_current_user(
    token: tp.Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_session),
) -> users_schemas.UserOutputDBSchema:
    logger.info("Try to get user from JWT token")
    username = get_username_from_token(token=token)
    logger.info("Try to get user by username")
    user = await users_crud.get_by_username(db, username=username)
    if user is None or not user.is_active:
        logger.error("User does not exists or not active")
        raise UnauthorizedException()

    logger.info("Success getting user from JWT token")
    return user
