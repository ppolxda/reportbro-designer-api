# -*- coding: utf-8 -*-
"""
@create: 2021-10-18 23:16:46.

@author: name

@desc: debug_env
"""
import os

import pytest

from reportbro_designer_api.clients import create_local_storage
from reportbro_designer_api.clients import create_s3_backend
from reportbro_designer_api.clients import create_s3_storage
from reportbro_designer_api.clients import get_meth_cli
from reportbro_designer_api.settings import settings

FPATH = os.path.abspath(os.path.dirname(__file__))

MINIO_URL = "s3://minioadmin:minioadmin@127.0.0.1:9000/reportbrotest"


@pytest.fixture(name="debug_env")
def fixture_debug_env():
    """Config test setting."""
    settings.DB_URL = MINIO_URL
    settings.STORAGE_URL = MINIO_URL
    settings.DEFAULT_TEMPLATE_PATH = FPATH + "/data/default_template.json"


@pytest.fixture
async def sqlite_cli(debug_env):
    """db_client."""
    assert debug_env is None
    settings.DB_URL = (
        "sqlite+aiosqlite:///./reportbro.db?db_isolation_level=READ UNCOMMITTED"
    )
    cli = get_meth_cli()
    await cli.clean_all()
    try:
        yield cli
    finally:
        await cli.clean_all()


@pytest.fixture
async def pgsql_cli(debug_env):
    """pgsql_cli."""
    assert debug_env is None
    settings.DB_URL = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/reportbro-test?db_isolation_level=READ UNCOMMITTED"
    cli = get_meth_cli()
    await cli.clean_all()
    try:
        yield cli
    finally:
        await cli.clean_all()


@pytest.fixture
async def mysql_cli(debug_env):
    """mysql_cli."""
    assert debug_env is None
    settings.DB_URL = "mysql+aiomysql://root:root@127.0.0.1:3306/reportbro-test?db_isolation_level=READ UNCOMMITTED"
    cli = get_meth_cli()
    await cli.clean_all()
    try:
        yield cli
    finally:
        await cli.clean_all()


@pytest.fixture
async def s3cli(debug_env):
    """s3_client."""
    assert debug_env is None
    cli = create_s3_backend(MINIO_URL)
    await cli.clean_all()
    try:
        yield cli
    finally:
        await cli.clean_all()


@pytest.fixture
async def s3storage(debug_env):
    """s3_client."""
    assert debug_env is None
    cli = create_s3_storage(MINIO_URL)
    await cli.clean_all()
    try:
        yield cli
    finally:
        await cli.clean_all()


@pytest.fixture
async def localstorage(debug_env):
    """s3_client."""
    assert debug_env is None
    cli = create_local_storage("file://out/reportpdf")
    await cli.clean_all()
    try:
        yield cli
    finally:
        await cli.clean_all()
 