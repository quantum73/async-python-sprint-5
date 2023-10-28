import tarfile
import typing as tp
import zipfile
from io import BytesIO
from pathlib import Path

import py7zr
from fastapi import Query
from fastapi.responses import Response, FileResponse, StreamingResponse

from core.enums import CompressionType


class CompressorProtocol(tp.Protocol):
    suffix: str | None
    media_type: str | None

    @staticmethod
    def prepare_file_path(file_path: str | Path) -> Path:
        return file_path if isinstance(file_path, Path) else Path(file_path)

    @classmethod
    def get_response(cls, *, file_path: str | Path) -> Response:
        raise NotImplementedError


class NoneCompressor(CompressorProtocol):
    suffix = ".zip"
    media_type = "application/x-zip-compressed"

    @classmethod
    def get_response(cls, *, file_path: str | Path) -> FileResponse:
        file_path = cls.prepare_file_path(file_path)
        return FileResponse(path=file_path, filename=file_path.name)


class ZipCompressor(CompressorProtocol):
    suffix = ".zip"
    media_type = "application/x-zip-compressed"

    @classmethod
    def get_response(cls, *, file_path: str | Path) -> StreamingResponse:
        file_path = cls.prepare_file_path(file_path)
        buffer = BytesIO()
        file_suffix = file_path.suffix
        zip_filename = file_path.name.replace(file_suffix, cls.suffix)
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(file_path.absolute())
            zip_file.close()

        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type=cls.media_type,
            headers={"Content-Disposition": f"attachment; filename=%s" % zip_filename},
        )


class TarCompressor(CompressorProtocol):
    suffix = ".tar.gz"
    media_type = "application/x-gtar"

    @classmethod
    def get_response(cls, *, file_path: str | Path) -> StreamingResponse:
        file_path = cls.prepare_file_path(file_path)
        buffer = BytesIO()
        file_suffix = file_path.suffix
        tar_filename = file_path.name.replace(file_suffix, cls.suffix)
        with tarfile.open(fileobj=buffer, mode="w:gz") as tar_file:
            tar_file.add(file_path.absolute(), arcname=file_path.name, recursive=False)
            tar_file.close()

        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type=cls.media_type,
            headers={"Content-Disposition": f"attachment; filename=%s" % tar_filename},
        )


class SevenZCompressor(CompressorProtocol):
    suffix = ".7z"
    media_type = "application/x-7z-compressed"

    @classmethod
    def get_response(cls, *, file_path: str | Path) -> StreamingResponse:
        file_path = cls.prepare_file_path(file_path)
        buffer = BytesIO()
        file_suffix = file_path.suffix
        seven_z_filename = file_path.name.replace(file_suffix, cls.suffix)
        with py7zr.SevenZipFile(file=buffer, mode="w") as archive_file:
            archive_file.write(file_path.absolute(), arcname=file_path.name)

        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type=cls.media_type,
            headers={"Content-Disposition": f"attachment; filename=%s" % seven_z_filename},
        )


COMPRESSORS_MAP = {
    CompressionType.zip.value: ZipCompressor,
    CompressionType.tar.value: TarCompressor,
    CompressionType.seven_z.value: SevenZCompressor,
}


def get_compressor(
    compression_type: tp.Annotated[CompressionType, Query(description="file compression type")],
) -> CompressorProtocol:
    return COMPRESSORS_MAP.get(compression_type, NoneCompressor)
