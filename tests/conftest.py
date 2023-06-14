# -*- coding: utf-8 -*-
"""
@create: 2021-10-18 23:16:46.

@author: name

@desc: debug_env
"""
import os

import pytest

from reportbro_designer_api.clients import create_db_client
from reportbro_designer_api.clients import create_s3_client
from reportbro_designer_api.settings import settings

FPATH = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(name="debug_env")
def fixture_debug_env():
    """Config test setting."""
    settings.MINIO_ENDPOINT_URL = "http://127.0.0.1:9000"
    settings.DEFAULT_TEMPLATE_PATH = FPATH + "/data/default_template.json"
    settings.MINIO_BUCKET = "reportbrotest-test"


@pytest.fixture
async def sqlite_cli(debug_env):
    """db_client."""
    assert debug_env is None
    settings.DB_URL = "sqlite+aiosqlite:///./reportbro.db"
    cli = create_db_client()
    await cli.clean_all()
    try:
        yield cli
    finally:
        await cli.clean_all()


@pytest.fixture
async def pgsql_cli(debug_env):
    """pgsql_cli."""
    assert debug_env is None
    settings.DB_URL = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/reportbro-test"
    )
    settings.DB_ISOLATION_LEVEL = "READ COMMITTED"
    cli = create_db_client()
    await cli.clean_all()
    try:
        yield cli
    finally:
        await cli.clean_all()


@pytest.fixture
async def mysql_cli(debug_env):
    """mysql_cli."""
    assert debug_env is None
    settings.DB_URL = "mysql+aiomysql://root:root@localhost:3306/reportbro-test"
    settings.DB_ISOLATION_LEVEL = "READ COMMITTED"
    cli = create_db_client()
    await cli.clean_all()
    try:
        yield cli
    finally:
        await cli.clean_all()


@pytest.fixture
async def s3cli(debug_env):
    """s3_client."""
    assert debug_env is None
    settings.DB_ISOLATION_LEVEL = "READ UNCOMMITTED"
    cli = create_s3_client()
    await cli.clean_all()
    try:
        yield cli
    finally:
        await cli.clean_all()
