# -*- coding: utf-8 -*-
"""
@create: 2023-06-12 17:20:00.

@author: luofuwen

@desc: clients
"""
import json
from functools import lru_cache
from urllib.parse import parse_qs
from urllib.parse import urlparse

from sqlalchemy.engine import Engine
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm.session import sessionmaker

from .backend import BackendBase
from .backend import DBBackend
from .backend import S3Backend
from .settings import settings
from .storage import LocalStorage
from .storage import S3Storage
from .storage import StorageMange
from .utils.report import ReportFontsLoader
from .utils.s3_client import S3Client

FONTS_LOADER = ReportFontsLoader(settings.FONTS_PATH)


def load_default_template():
    """Load default template."""
    tmp_path = settings.STATIC_PATH + "/default_template.json"
    if settings.DEFAULT_TEMPLATE_PATH:
        tmp_path = settings.DEFAULT_TEMPLATE_PATH

    with open(tmp_path, "r", encoding="utf8") as fss:
        defdata = fss.read()
        defdata = json.loads(defdata)

    return defdata


def create_s3_client(db_url) -> S3Client:
    """Create s3 client."""
    url_ = urlparse(db_url)

    scheme = "http"
    if url_.scheme == "ss3":
        scheme = "https"

    if url_.port:
        endpoint_url = f"{scheme}://{url_.hostname}:{url_.port}"
    else:
        endpoint_url = f"{scheme}://{url_.hostname}"

    query_params = parse_qs(url_.query)
    region_name = query_params.get("region_name", ["us-west-1"])[0]

    return S3Client(
        aws_access_key_id=url_.username or "minioadmin",
        aws_secret_access_key=url_.password or "minioadmin",
        endpoint_url=endpoint_url,
        region_name=region_name or "us-west-1",
        bucket=url_.path[1:] or "reportbro",
    )


def __create_db_engine(db_url: str, is_async=True):
    """Create Datebase engin."""
    if is_async:
        create_engine_ = create_async_engine
    else:
        create_engine_ = create_engine

    db_url_ = urlparse(db_url)
    query_params = parse_qs(db_url_.query)
    db_pool_size = int(query_params.get("db_pool_size", [5])[0])
    db_pool_timeout = int(query_params.get("db_pool_timeout", [30])[0])
    db_pool_recycle = int(query_params.get("db_pool_recycle", [1800])[0])
    db_max_overflow = int(query_params.get("db_max_overflow", [10])[0])
    db_isolation_level = query_params.get("db_isolation_level", ["READ UNCOMMITTED"])[0]
    print_sql = bool(query_params.get("print_sql", [False])[0])
    db_url = db_url.split("?")[0]

    if settings.DB_URL.startswith("sqlite"):
        engine = create_engine_(
            db_url,
            echo=print_sql,
            hide_parameters=print_sql,
            isolation_level=db_isolation_level,
            future=True,
        )
    else:
        engine = create_engine_(
            db_url,
            pool_pre_ping=True,
            hide_parameters=not print_sql,
            echo=print_sql,
            isolation_level=db_isolation_level,
            pool_size=db_pool_size,
            pool_timeout=db_pool_timeout,
            pool_recycle=db_pool_recycle,
            max_overflow=db_max_overflow,
            future=True,
        )
    return engine


def create_db_sync_engine(db_url: str) -> Engine:
    """Create Datebase Async engine."""
    engine = __create_db_engine(db_url, is_async=False)
    assert isinstance(engine, Engine)
    return engine


def create_db_async_engine(db_url: str) -> AsyncEngine:
    """Create Datebase Async engine."""
    engine = __create_db_engine(db_url, is_async=True)
    assert isinstance(engine, AsyncEngine)
    return engine


def create_db_sessionmaker(db_url: str) -> sessionmaker:
    """Create Datebase client."""
    engine = create_db_sync_engine(db_url)
    return sessionmaker(
        autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
    )


@lru_cache
def get_db_sessionmaker():
    """Get Datebase client."""
    engine = create_db_sync_engine(settings.db_url_sync)
    return sessionmaker(
        autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
    )


def create_db_asyncsessionmaker(db_url: str) -> async_sessionmaker:
    """Create Datebase client."""
    engine = create_db_async_engine(db_url)
    return async_sessionmaker(
        autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
    )


def create_db_backend(db_url: str) -> DBBackend:
    """Create Datebase client."""
    asyncsessionmaker = create_db_asyncsessionmaker(db_url)
    defdata = load_default_template()
    return DBBackend(
        asyncsessionmaker,
        default_template=defdata,
    )


def create_s3_backend(db_url: str) -> S3Backend:
    """Get s3 client."""
    defdata = load_default_template()
    s3cli = create_s3_client(db_url)
    return S3Backend(
        s3cli,
        default_template=defdata,
    )


@lru_cache()
def get_meth_cli() -> BackendBase:
    """获取连接."""
    if settings.DB_URL.startswith("s3://") or settings.DB_URL.startswith("ss3://"):
        return create_s3_backend(settings.DB_URL)
    else:
        return create_s3_backend(settings.DB_URL)


def create_local_storage(db_url):
    """Create local storage."""
    assert settings.STORAGE_URL.startswith("file://")
    url_ = urlparse(db_url)
    query_params = parse_qs(url_.query)
    storage_local_ttl = int(query_params.get("storage_local_ttl", [5])[0])
    return LocalStorage(url_.path or "./data", storage_local_ttl)


def create_s3_storage(db_url: str):
    """Create S3 storage."""
    s3cli = create_s3_client(db_url)
    return S3Storage(s3cli)


@lru_cache()
def get_storage_cli():
    """Get Storage client."""
    if settings.STORAGE_URL.startswith("file://"):
        return create_local_storage(settings.STORAGE_URL)
    elif settings.STORAGE_URL.startswith("s3://") or settings.STORAGE_URL.startswith(
        "ss3://"
    ):
        return create_s3_storage(settings.STORAGE_URL)
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
