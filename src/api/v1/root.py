from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from services import root as root_services

root_router = APIRouter()


@root_router.get("/ping", status_code=status.HTTP_200_OK)
async def ping_services(db: AsyncSession = Depends(get_session)):
    database_info = await root_services.database_access_time(db)
    return {database_info.name: database_info.access_time}
