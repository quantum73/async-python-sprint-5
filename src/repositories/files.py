from uuid import UUID

from sqlalchemy import or_, desc, text, and_, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.enums import OrderByType
from db.models import File
from .base import DatabaseRepository, PydanticSchemaType, ModelType


class FileRepository(DatabaseRepository[File, PydanticSchemaType]):
    async def get_file_by_path(self, db: AsyncSession, *, target_path: str) -> ModelType | None:
        statement = select(self._model).where(self._model.path == target_path)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_file_by_id_or_path(self, db: AsyncSession, *, idx: str | UUID | None, path: str) -> ModelType | None:
        statement = select(self._model).where(or_(self._model.id == idx, self._model.path == path))
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_multi_by_user(
        self, db: AsyncSession, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        statement = (
            select(self._model)
            .where(self._model.user_id == user_id)
            .order_by(desc("created_at"))
            .offset(skip)
            .limit(limit)
        )
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def search_files(
        self,
        db: AsyncSession,
        *,
        path: str,
        extension: str,
        order_by_field: str,
        order_by_type: OrderByType,
        limit: int,
    ) -> list[ModelType]:
        order_by_func = asc if order_by_type == OrderByType.ascending else desc
        statement = (
            select(self._model)
            .where(and_(self._model.path.startswith(path), self._model.name.endswith(extension)))
            .order_by(order_by_func(text(order_by_field)))
            .limit(limit)
        )
        results = await db.execute(statement=statement)
        return results.scalars().all()


files_crud: FileRepository = FileRepository(File)
