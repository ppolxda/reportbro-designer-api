# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 17:50:25.

@author: ppolxda

@desc: Settings
"""
import os
from functools import lru_cache

import pkg_resources
from pydantic import BaseSettings
from sqlalchemy.engine.url import make_url

TEMPLATES_PATH = pkg_resources.resource_filename("reportbro_designer_api", "templates")
STATIC_PATH = pkg_resources.resource_filename("reportbro_designer_api", "static")
FONTS_PATH = os.path.join(STATIC_PATH, "fonts")
PROD = os.environ.get("PROD", "")


class Settings(BaseSettings):
    """Settings."""

    SHOW_DOC: bool = bool(os.environ.get("SHOW_DOC", "true") == "true")
    IS_DEBUG: bool = bool(os.environ.get("IS_DEBUG", "false") == "true")
    STATIC_PATH: str = STATIC_PATH
    TEMPLATES_PATH: str = TEMPLATES_PATH
    FONTS_PATH: str = FONTS_PATH
    DEFAULT_TEMPLATE_PATH: str = ""
    PDF_TITLE: str = "report"
    PDF_DEFAULT_FONT: str = "helvetica"
    PDF_LOCALE: str = "en_us"

    ROOT_PATH: str = ""
    ROOT_PATH_IN_SERVERS: bool = True

    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_ENDPOINT_URL: str = "http://127.0.0.1:9000"
    MINIO_BUCKET: str = "reportbro"
    # MINIO_SITE_NAME: str = "reportbro-s3"
    MINIO_SITE_REGION: str = "us-west-1"

    DOWNLOAD_TIMEOUT: int = 180

    # sqlite+aiosqlite:///./reportbro.db
    # mysql+aiomysql://root:root@localhost/reportbro
    # postgresql+asyncpg://postgres:postgres@localhost:5432/reportbro
    DB_URL: str = "sqlite+aiosqlite:///./reportbro.db"
    DB_POOL_SIZE: int = 5
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_MAX_OVERFLOW: int = 10
    DB_ISOLATION_LEVEL: str = "READ UNCOMMITTED"
    PRINT_SQL: bool = False

    BACKEND_MODE: str = "s3"
    STORAGE_MODE: str = "s3"
    STORAGE_LOCAL_TTL: int = 30 * 60
    STORAGE_LOCAL_PATH: str = ""

    @property
    def db_url_mark(self):
        """Show the mark db config."""
        return make_url(settings.DB_URL)

    @property
    def db_url_sync_mark(self):
        """DB Async url to Sync url."""
        return make_url(settings.db_url_sync)

    @property
    def db_url_sync(self):
        """DB Async url to Sync url."""
        db_url = settings.DB_URL.replace("+aiosqlite", "")
        db_url = db_url.replace("aiomysql", "pymysql")
        db_url = db_url.replace("asyncpg", "psycopg2")
        return db_url

    def format_print(self):
        """Print config."""
        # await database.connect()
        log = ["--------------------------------------"]
        for key, val in self.dict().items():
            if key in ["MINIO_SECRET_KEY", "MINIO_ACCESS_KEY"]:
                continue

            if (
                key.endswith("URI")
                or key.endswith("URL")
                or key.endswith("KEY")
                and "sqlite" not in val
            ):
                log.append(f"[{key:23s}]: {repr(make_url(val))}")
            else:
                log.append(f"[{key:23s}]: {val}")

        log.append("--------------------------------------")
        return log

    class Config:
        """Config."""

        env_file = ".env." + PROD if PROD else ".env"


@lru_cache()
def get_settings():
    """Get settings."""
    return Settings()


settings = Settings()
