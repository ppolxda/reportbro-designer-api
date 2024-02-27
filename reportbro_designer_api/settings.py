# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 17:50:25.

@author: ppolxda

@desc: Settings
"""
import os
from functools import lru_cache

import pkg_resources
from pydantic_settings import BaseSettings
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
    PAGE_LIMIT: int = 1000

    ROOT_PATH: str = ""
    ROOT_PATH_IN_SERVERS: bool = True

    DOWNLOAD_TIMEOUT: int = 180
    DOWNLOAD_TIMEOUT: int = 180
    PROCESS_POOL_SIZE: int = 0

    # s3://minioadmin:minioadmin@127.0.0.1:9000/reportbro
    # ss3://minioadmin:minioadmin@127.0.0.1:9000/reportbro
    # sqlite+aiosqlite:///./reportbro.db
    # mysql+aiomysql://root:root@localhost/reportbro
    # postgresql+asyncpg://postgres:postgres@localhost:5432/reportbro
    DB_URL: str = "sqlite+aiosqlite:///./data/reportbro.db?re=aa"
    STORAGE_URL: str = "file://./data?storage_local_ttl=180"

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
