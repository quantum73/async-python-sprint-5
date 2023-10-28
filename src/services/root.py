import time
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True, slots=True)
class ServiceInfo:
    name: str
    access_time: float | None = None


async def database_access_time(db: AsyncSession) -> ServiceInfo:
    start = time.monotonic()
    try:
        await db.execute(text("SELECT 1"))
    finally:
        access_time = time.monotonic() - start
        access_time = round(access_time, 3)

    return ServiceInfo(name="db", access_time=access_time)
