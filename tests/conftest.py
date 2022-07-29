# -*- coding: utf-8 -*-
"""
@create: 2021-10-18 23:16:46.

@author: name

@desc: debug_env
"""
import os
from uuid import uuid1
from uuid import uuid4

import pytest

from reportbro_designer_api import settings

FPATH = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(name="debug_env")
def fixture_debug_env(monkeypatch):
    """Config test setting."""
    monkeypatch.setenv(
        "MINIO_ENDPOINT_URL",
        "http://127.0.0.1:9000",
        prepend=None,
    )
    monkeypatch.setenv(
        "DEFAULT_TEMPLATE_PATH", FPATH + "/data/default_template.json", prepend=None
    )
    bucket_id = str(uuid1()).replace("-", "")
    monkeypatch.setenv("MINIO_BUCKET", f"reportbrotest-{bucket_id}", prepend=None)
    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(settings, "settings", settings.Settings())


@pytest.fixture
def s3cli(debug_env):
    """s3_client."""
    assert debug_env is None
    settings.get_s3_client.cache_clear()
    cli = settings.create_s3_client()
    cli.clear_bucket()
    yield cli
    cli.clear_bucket()
