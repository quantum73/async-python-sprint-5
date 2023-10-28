import logging
import typing as tp
from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile, Body
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from core import exceptions
from core.config import settings
from core.utils import is_valid_uuid4, async_save_file
from repositories.base import ModelType, PydanticSchemaType
from repositories.files import files_crud

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PreparedFileObject:
    path: str
    obj: UploadFile = field(repr=False)

    size: int = field(init=False, repr=False)
    name: str = field(init=False, repr=False)
    full_file_path: str = field(init=False, repr=False)

    @tp.no_type_check
    def __post_init__(self) -> None:
        self.size = self.obj.size
        file_name = self.obj.filename

        path = Path(self.path.strip("/"))
        full_path = settings.app.storage_directory / path
        if not bool(full_path.suffix):
            full_path = full_path / file_name
            path = path / file_name
        else:
            file_name = full_path.name

        full_path.parent.mkdir(parents=True, exist_ok=True)
        self.name = file_name
        self.full_file_path = full_path.absolute()
        self.path = f"/{path}"


def get_prepared_file_from_body(file: UploadFile, path: tp.Annotated[str, Body(embed=True)]) -> PreparedFileObject:
    return PreparedFileObject(path=path, obj=file)


async def get_absolute_storage_file_path(file_obj: PreparedFileObject) -> Path:
    file_path = file_obj.path.strip("/")
    return settings.app.storage_directory / file_path


async def create_file(db: AsyncSession, *, prepared_file_object: PreparedFileObject, user_id: str | UUID) -> ModelType:
    logger.info(f"Create file by User(#{user_id})")
    try:
        await async_save_file(file_obj=prepared_file_object.obj, file_path=prepared_file_object.full_file_path)
    except Exception as err:
        logger.exception(err)
        raise exceptions.BadRequestException("Invalid file")

    obj_in = {
        "name": prepared_file_object.name,
        "path": prepared_file_object.path,
        "size": prepared_file_object.size,
        "user_id": user_id,
    }
    file_in_db = await files_crud.create(db, obj_in=obj_in)
    return file_in_db


async def get_file_by_id(db: AsyncSession, *, idx: str) -> ModelType | None:
    logger.info(f"Get file by {idx} id")
    file: ModelType | None = await files_crud.get(db, idx=idx)
    return file


async def get_file_by_path(db: AsyncSession, *, target_path: str) -> ModelType | None:
    logger.info(f'Get file by "{target_path}" path')
    file: ModelType | None = await files_crud.get_file_by_path(db, target_path=target_path)
    return file


async def get_file_by_id_or_path(db: AsyncSession, *, value: str) -> ModelType | None:
    logger.info(f'Get file by "{value}" id or path')
    idx = value if is_valid_uuid4(value) else None
    path = value
    file: ModelType | None = await files_crud.get_file_by_id_or_path(db, idx=idx, path=path)
    return file


async def get_files_list(db: AsyncSession, *, skip: int, limit: int) -> list[ModelType]:
    logger.info(f"Get files list [skip={skip};limit={limit}]")
    files = await files_crud.get_multi(db, skip=skip, limit=limit)
    return files


async def get_user_files(db: AsyncSession, *, user_id: str, skip: int, limit: int) -> list[ModelType]:
    logger.info(f"Get User(#{user_id}) files [skip={skip};limit={limit}]")
    files: list[ModelType] = await files_crud.get_multi_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return files


async def search_files(db: AsyncSession, *, search_options: PydanticSchemaType | dict) -> list[ModelType]:
    logger.info("Search files by options")
    search_options_as_dict = jsonable_encoder(search_options, exclude_unset=True)
    options = search_options_as_dict["options"]
    order_by_data = options["order_by"]
    try:
        files: list[ModelType] = await files_crud.search_files(
            db,
            path=options["path"],
            extension=options["extension"],
            order_by_field=order_by_data["field"],
            order_by_type=order_by_data["type"],
            limit=options["limit"],
        )
    except Exception as err:
        logger.exception(err)
        raise exceptions.BadRequestException("Invalid search data")
    else:
        return files
