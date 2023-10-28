import typing as tp
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.base import Base

ModelType = tp.TypeVar("ModelType", bound=Base)
PydanticSchemaType = tp.TypeVar("PydanticSchemaType", bound=BaseModel)


class Repository:
    def get(self, *args, **kwargs) -> tp.Any:  # type: ignore
        raise NotImplementedError

    def get_multi(self, *args, **kwargs) -> tp.Any:  # type: ignore
        raise NotImplementedError

    def create(self, *args, **kwargs) -> tp.Any:  # type: ignore
        raise NotImplementedError

    def update(self, *args, **kwargs) -> tp.Any:  # type: ignore
        raise NotImplementedError

    def delete(self, *args, **kwargs) -> tp.Any:  # type: ignore
        raise NotImplementedError


class DatabaseRepository(Repository, tp.Generic[ModelType, PydanticSchemaType]):
    def __init__(self, model: tp.Type[ModelType]) -> None:
        self._model = model

    async def get(self, db: AsyncSession, *, idx: str | UUID) -> ModelType | None:
        statement = select(self._model).where(self._model.id == idx)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        statement = select(self._model).offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: PydanticSchemaType | dict) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in, exclude_unset=True)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: ModelType, obj_in: PydanticSchemaType | dict) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in, exclude_unset=True)
        statement = update(self._model).where(self._model.id == db_obj.id).values(**obj_in_data).returning(self._model)
        await db.execute(statement=statement)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, idx: int) -> None:
        statement = delete(self._model).where(self._model.id == idx)
        await db.execute(statement=statement)
        await db.commit()
