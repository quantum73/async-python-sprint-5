import typing as tp

from fastapi import HTTPException, status

from core.config import settings


class BaseHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: tp.Any = None, headers: tp.Dict[str, str] | None = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(BaseHTTPException):
    entity_name: str

    def __init__(self, idx: int | str, headers: tp.Dict[str, str] | None = None):
        detail = f"{self.entity_name} not found. ID: {idx}"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers)


class BadRequestException(BaseHTTPException):
    base_detail: str = "Invalid data"

    def __init__(self, detail: tp.Any = None, headers: tp.Dict[str, str] | None = None):
        if detail is None:
            detail = self.base_detail
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, headers=headers)


class UnauthorizedException(BaseHTTPException):
    base_detail: str = "Could not validate credentials"
    base_headers: tp.Dict[str, str] = {"WWW-Authenticate": settings.jwt.token_type}

    def __init__(self, detail: tp.Any = None, headers: tp.Dict[str, str] | None = None):
        if detail is None:
            detail = self.base_detail
        if headers is None:
            headers = self.base_headers
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers)


class UserNotFoundException(NotFoundException):
    entity_name: str = "User"


class FileNotFoundException(NotFoundException):
    entity_name: str = "File"
