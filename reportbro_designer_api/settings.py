# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 17:50:25.

@author: ppolxda

@desc: Settings
"""
import json
import os
from functools import lru_cache

import pkg_resources
from pydantic import BaseSettings

from reportbro_designer_api.utils.report import ReportFontsLoader
from reportbro_designer_api.utils.s3 import ReportbroS3Client

# from sqlalchemy.engine.url import make_url

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
    OPENAPI_URL: str = ""
    PDF_TITLE: str = "report"
    PDF_DEFAULT_FONT: str = "helvetica"
    PDF_LOCALE: str = "en_us"

    ROOT_PATH: str = ""
    ROOT_PATH_IN_SERVERS: bool = bool(
        os.environ.get("ROOT_PATH_IN_SERVERS", "false") == "true"
    )

    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_ENDPOINT_URL: str = "http://127.0.0.1:9000"
    MINIO_BUCKET: str = "reportbro"
    # MINIO_SITE_NAME: str = "reportbro-s3"
    MINIO_SITE_REGION: str = "us-west-1"

    def format_print(self):
        """Print config."""
        # await database.connect()
        log = ["--------------------------------------"]
        for key, val in self.dict().items():
            if key in ["MINIO_SECRET_KEY"]:
                continue

            # if key in ["REDIS_URL", "MONGODB_URL"]:
            #     log.append(f"[{key:23s}]: {repr(make_url(val))}")
            # else:
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


@lru_cache()
def get_s3_client() -> ReportbroS3Client:
    """Get s3 client."""
    with open(
        settings.STATIC_PATH + "/default_template.json", "r", encoding="utf8"
    ) as fss:
        defdata = fss.read()
        defdata = json.loads(defdata)

    return ReportbroS3Client(
        settings.MINIO_ACCESS_KEY,
        settings.MINIO_SECRET_KEY,
        endpoint_url=settings.MINIO_ENDPOINT_URL,
        region_name=settings.MINIO_SITE_REGION,
        bucket=settings.MINIO_BUCKET,
        default_template=defdata,
    )


settings = Settings()
FONTS_LOADER = ReportFontsLoader(settings.FONTS_PATH)
