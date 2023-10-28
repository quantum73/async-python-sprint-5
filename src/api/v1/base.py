from fastapi import APIRouter

from api.v1.files import files_router
from api.v1.root import root_router
from api.v1.users import user_router

api_router = APIRouter()

api_router.include_router(root_router, tags=["root"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(files_router, prefix="/files", tags=["files"])
