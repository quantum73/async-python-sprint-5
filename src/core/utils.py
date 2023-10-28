import typing as tp
import uuid
from dataclasses import dataclass
from pathlib import Path

import aiofiles
from passlib.context import CryptContext


class PasswordHasher:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, *, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)


@dataclass(frozen=True, slots=True)
class Paginator:
    offset: int
    limit: int


def query_paginator(offset: int = 0, limit: int = 10) -> Paginator:
    return Paginator(offset=offset, limit=limit)


async def async_save_file(file_obj: tp.Any, *, file_path: str | Path) -> None:
    if isinstance(file_path, Path):
        file_path = file_path.absolute()

    async with aiofiles.open(file_path, "wb") as out_file:
        while content := await file_obj.read(1024):
            await out_file.write(content)


def is_valid_uuid4(value: tp.Any) -> bool:
    try:
        uuid.UUID(str(value), version=4)
        return True
    except ValueError:
        return False
