import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, RedirectResponse

from api.v1 import base
from core.config import settings

app = FastAPI(
    title=settings.app.title,
    version=settings.app.version,
    docs_url=settings.app.docs_url,
    openapi_url=settings.app.openapi_url,
    default_response_class=ORJSONResponse,
)
app.add_route("/", RedirectResponse(url=settings.app.docs_url))
app.include_router(base.api_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.app.host, port=settings.app.port)
