# -*- coding: utf-8 -*-
"""
@create: 2021-10-18 23:16:46.

@author: name

@desc: debug_env
"""
import os

import pytest

from reportbro_designer_api import settings

FPATH = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def debug_env(monkeypatch):
    """Config test setting."""
    monkeypatch.setenv(
        "MINIO_ENDPOINT_URL",
        "http://127.0.0.1:9000",
        prepend=None,
    )
    monkeypatch.setenv("MINIO_BUCKET", "reportbrotest", prepend=None)
    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(settings, "settings", settings.Settings())
