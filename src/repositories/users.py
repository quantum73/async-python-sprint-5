from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from .base import DatabaseRepository, PydanticSchemaType, ModelType


class UserRepository(DatabaseRepository[User, PydanticSchemaType]):
    async def get_by_username(self, db: AsyncSession, *, username: str) -> ModelType | None:
        statement = select(self._model).where(self._model.username == username)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()


users_crud: UserRepository = UserRepository(User)
