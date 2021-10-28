from fastapi import FastAPI
from .routers import api_root
from .routers.v1.api_user_keys import user_keys
from .routers.v1.api_file_keys import file_keys

def api_registry(app: FastAPI):
    app.include_router(api_root.router, prefix="/v1")
    app.include_router(user_keys.router, prefix="/v1/keys")
    app.include_router(file_keys.router, prefix="/v1/keys")

