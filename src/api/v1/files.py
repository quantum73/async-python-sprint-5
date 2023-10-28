import typing as tp

from fastapi import APIRouter, Depends, status, Body, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from core import exceptions
from core.compressors import CompressorProtocol, get_compressor
from core.config import settings
from core.utils import Paginator, query_paginator
from db import get_session
from schemas import files as files_schemas, users as users_schemas
from services import files as files_services, users as users_services
from services.files import PreparedFileObject

files_router = APIRouter()


@files_router.get(
    "/list",
    response_model=files_schemas.FileListSchema,
    status_code=status.HTTP_200_OK,
)
async def files_list(  # type: ignore
    paginator: tp.Annotated[Paginator, Depends(query_paginator)],
    current_user: tp.Annotated[users_schemas.UserOutputDBSchema, Depends(users_services.get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    user_id = current_user.id
    files = await files_services.get_user_files(  # type: ignore
        db,
        user_id=user_id.hex,
        skip=paginator.offset,
        limit=paginator.limit,
    )
    return {
        "account_id": user_id,
        "files": files,
        "skip": paginator.offset,
        "limit": paginator.limit,
    }


@files_router.post(
    "/upload",
    response_model=files_schemas.FileOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(  # type: ignore
    prepared_file_object: tp.Annotated[PreparedFileObject, Depends(files_services.get_prepared_file_from_body)],
    current_user: tp.Annotated[users_schemas.UserOutputDBSchema, Depends(users_services.get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    file_in_db = await files_services.create_file(  # type: ignore
        db,
        prepared_file_object=prepared_file_object,
        user_id=current_user.id,
    )
    return file_in_db


@files_router.get(
    "/download",
    response_class=Response,
    status_code=status.HTTP_200_OK,
)
async def download_file(  # type: ignore
    path: tp.Annotated[str, Query(min_length=1, description="Path to file or File ID")],
    compressor: tp.Annotated[CompressorProtocol, Depends(get_compressor)],
    current_user: tp.Annotated[users_schemas.UserOutputDBSchema, Depends(users_services.get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    file_obj = await files_services.get_file_by_id_or_path(db, value=path)  # type: ignore
    if file_obj is None:
        raise exceptions.FileNotFoundException(path)

    full_path = settings.app.storage_directory / file_obj.path
    return compressor.get_response(file_path=full_path)


@files_router.post(
    "/search",
    response_model=files_schemas.MatchedSearchOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def search_files(  # type: ignore
    search_options: tp.Annotated[files_schemas.SearchDataSchema, Body()],
    current_user: tp.Annotated[users_schemas.UserOutputDBSchema, Depends(users_services.get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    files = await files_services.search_files(db, search_options=search_options)  # type: ignore
    return {"matches": files}
