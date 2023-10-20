# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 17:42:41.

@author: ppolxda

@desc: web main
"""
import traceback
from contextlib import asynccontextmanager
from botocore.exceptions import ClientError
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from .errors import ReportbroError
from .router import router
from .settings import settings
from .utils.logger import LOGGER
from .utils.model import ErrorResponse
from .version import __VERSION__
from .clients import get_storage_mange


def get_app() -> FastAPI:
    """Fastapi app."""

    def print_var():
        # await database.connect()
        LOGGER.info("--------------------------------------")
        for i in rapp.router.routes:
            if not hasattr(i, "methods"):
                continue

            LOGGER.info(f'[{str(",".join(i.methods)):15s}]: {i.name:30s}: {i.path}')  # type: ignore

        # LOGGER.info("--------------------------------------")
        LOGGER.info("\n".join(settings.format_print()))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        print_var()
        yield
        LOGGER.info("service shutdown")

    rapp = FastAPI(
        title="Reportbro designer server",
        description="Reportbro designer server",
        version=__VERSION__,
        openapi_prefix=settings.ROOT_PATH,
        openapi_url="/openapi.json" if settings.SHOW_DOC else None,
        docs_url="/docs" if settings.SHOW_DOC else None,
        redoc_url="/redoc" if settings.SHOW_DOC else None,
        root_path=settings.ROOT_PATH,
        root_path_in_servers=settings.ROOT_PATH_IN_SERVERS,
        debug=settings.IS_DEBUG,
        lifespan=lifespan,
        servers=[
            {
                "url": settings.ROOT_PATH if settings.ROOT_PATH else "/",
                "description": "localhost",
            },
        ],
    )
    rapp.mount("/static", StaticFiles(directory=settings.STATIC_PATH), name="static")
    rapp.include_router(router)

    @rapp.exception_handler(ReportbroError)
    async def report_exception_handler(request: Request, exc: ReportbroError):
        assert request
        LOGGER.warning("report_error[%s]", exc)
        return JSONResponse(
            ErrorResponse(code=HTTP_503_SERVICE_UNAVAILABLE, error=str(exc)).dict(),
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
        )

    @rapp.exception_handler(ClientError)
    async def s3_exception_handler(request: Request, exc: ClientError):
        assert request
        if exc.response.get("Error", {}).get("Code", "") == "NoSuchKey":
            return JSONResponse(
                ErrorResponse(code=HTTP_404_NOT_FOUND, error="NoSuchKey").dict(),
                status_code=HTTP_404_NOT_FOUND,
            )
        else:
            LOGGER.warning("s3_error[%s][%s]", exc, traceback.format_exc())
            return JSONResponse(
                ErrorResponse(
                    code=HTTP_503_SERVICE_UNAVAILABLE, error="NoSuchKey"
                ).dict(),
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
            )

    @rapp.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        assert request
        LOGGER.warning("http_error[%s]", exc.detail)
        return JSONResponse(
            ErrorResponse(code=exc.status_code, error=exc.detail).dict(),
            status_code=exc.status_code,
        )

    @rapp.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        assert request
        LOGGER.error("unknow_error[%s]%s", exc, traceback.format_exc())
        return JSONResponse(
            ErrorResponse(
                code=HTTP_500_INTERNAL_SERVER_ERROR, error="unknow error"
            ).dict(),
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return rapp


app = get_app()
