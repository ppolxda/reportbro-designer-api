# -*- coding: utf-8 -*-
"""
@create: 2023-06-12 17:20:00.

@author: luofuwen

@desc: clients
"""
import json
from functools import lru_cache

from sqlalchemy.engine import Engine
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm.session import sessionmaker

from .backend import BackendBase
from .backend import DBBackend
from .backend import S3Backend
from .errors import ClientParamsError
from .settings import settings
from .storage import LocalStorage
from .storage import S3Storage
from .storage import StorageMange
from .utils.report import ReportFontsLoader

FONTS_LOADER = ReportFontsLoader(settings.FONTS_PATH)


@lru_cache()
def get_s3_client() -> S3Backend:
    """Get s3 client."""
    return create_s3_client()


def load_default_template():
    """Load default template."""
    tmp_path = settings.STATIC_PATH + "/default_template.json"
    if settings.DEFAULT_TEMPLATE_PATH:
        tmp_path = settings.DEFAULT_TEMPLATE_PATH

    with open(tmp_path, "r", encoding="utf8") as fss:
        defdata = fss.read()
        defdata = json.loads(defdata)

    return defdata


def create_s3_client() -> S3Backend:
    """Create s3 client."""
    defdata = load_default_template()
    return S3Backend(
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        endpoint_url=settings.MINIO_ENDPOINT_URL,
        region_name=settings.MINIO_SITE_REGION,
        bucket=settings.MINIO_BUCKET,
        default_template=defdata,
    )


@lru_cache()
def get_db_client():
    """Get Datebase client."""
    return create_db_client()


def __create_db_engine(is_async=True):
    """Create Datebase engin."""
    if is_async:
        create_engine_ = create_async_engine
        db_url = settings.DB_URL
    else:
        create_engine_ = create_engine
        db_url = settings.db_url_sync

    if settings.DB_URL.startswith("sqlite"):
        engine = create_engine_(
            db_url,
            echo=settings.PRINT_SQL,
            hide_parameters=not settings.PRINT_SQL,
            isolation_level=settings.DB_ISOLATION_LEVEL,
            future=True,
        )
    else:
        engine = create_engine_(
            db_url,
            pool_pre_ping=True,
            hide_parameters=not settings.PRINT_SQL,
            echo=settings.PRINT_SQL,
            isolation_level=settings.DB_ISOLATION_LEVEL,
            pool_size=settings.DB_POOL_SIZE,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            future=True,
        )
    return engine


def create_db_sync_engine() -> Engine:
    """Create Datebase Async engine."""
    engine = __create_db_engine(is_async=False)
    assert isinstance(engine, Engine)
    return engine


def create_db_async_engine() -> AsyncEngine:
    """Create Datebase Async engine."""
    engine = __create_db_engine(is_async=True)
    assert isinstance(engine, AsyncEngine)
    return engine


def create_db_sessionmaker() -> sessionmaker:
    """Create Datebase client."""
    engine = create_db_sync_engine()
    return sessionmaker(
        autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
    )


def create_db_asyncsessionmaker() -> async_sessionmaker:
    """Create Datebase client."""
    engine = create_db_async_engine()
    return async_sessionmaker(
        autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
    )


def create_db_client() -> DBBackend:
    """Create Datebase client."""
    asyncsessionmaker = create_db_asyncsessionmaker()
    defdata = load_default_template()
    return DBBackend(
        asyncsessionmaker,
        default_template=defdata,
    )


@lru_cache()
def get_meth_cli() -> BackendBase:
    """获取连接."""
    if settings.BACKEND_MODE == "s3":
        return get_s3_client()
    elif settings.BACKEND_MODE == "db":
        return get_db_client()
    else:
        raise ClientParamsError(f"Get Client Meth Error [{settings.BACKEND_MODE}]")


def create_local_storage():
    """Create local storage."""
    return LocalStorage(
        settings.STORAGE_LOCAL_PATH,
        settings.STORAGE_LOCAL_TTL,
    )


def create_s3_storage():
    """Create S3 storage."""
    return S3Storage(
        settings.MINIO_ACCESS_KEY,
        settings.MINIO_SECRET_KEY,
        endpoint_url=settings.MINIO_ENDPOINT_URL,
        region_name=settings.MINIO_SITE_REGION,
        bucket=settings.MINIO_BUCKET,
    )


@lru_cache()
def get_storage_cli():
    """Get Storage client."""
    if settings.STORAGE_MODE == "local":
        return create_local_storage()
    elif settings.STORAGE_MODE == "s3":
        return create_s3_storage()
    else:
        raise TypeError("STORAGE_MODE invaild")


def create_s3_storage_manage():
    """Create S3 storage manage."""
    cli = get_storage_cli()
    return StorageMange(cli)


@lru_cache()
def get_storage_mange():
    """Get S3 storage manage."""
    return create_s3_storage_manage()
