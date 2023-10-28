from datetime import datetime
from uuid import UUID

from fastapi import UploadFile
from pydantic import BaseModel

from core.enums import OrderByType


class FileInputSchema(BaseModel):
    path: str
    file: UploadFile


class FileOutputSchema(BaseModel):
    id: UUID
    name: str
    path: str
    size: int
    is_downloadable: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FileListSchema(BaseModel):
    account_id: UUID
    skip: int
    limit: int
    files: list[FileOutputSchema]


class OrderBySchema(BaseModel):
    field: str
    type: OrderByType


class SearchOptionsSchema(BaseModel):
    path: str
    extension: str
    order_by: OrderBySchema
    limit: int = 10


class SearchDataSchema(BaseModel):
    options: SearchOptionsSchema
    # Я так и не понял что чего можно использовать "query" :)
    # query: str | None = None


class MatchedSearchOutputSchema(BaseModel):
    matches: list[FileOutputSchema]
