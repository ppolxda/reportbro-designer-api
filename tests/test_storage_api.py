# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 18:42:56.

@author: ppolxda

@desc: test s3 client api
"""
import asyncio
import os

import pytest

from reportbro_designer_api.storage import LocalStorage
from reportbro_designer_api.storage import S3Storage
from reportbro_designer_api.storage import StorageBase


async def storage_test(cli: StorageBase):
    """Test reportbro Storage api function."""
    s3_key = "s3://tests/data/testfile.pdf"
    fspath = "tests/data/testfile.pdf"
    with open(fspath, "rb") as fs:
        data = fs.read()

    await cli.put_file(s3_key, data)
    data_2 = await cli.get_file(s3_key)
    assert data == data_2


@pytest.mark.asyncio
async def test_s3_api(s3storage: S3Storage):
    """Test s3 reportbro api function."""
    await storage_test(s3storage)


@pytest.mark.asyncio
async def test_local_api(localstorage: LocalStorage):
    """Test s3 reportbro api function."""
    localstorage.storage_ttl = 5
    await storage_test(localstorage)
    assert os.path.exists("./upload/data/testfile.pdf")
    await asyncio.sleep(6)
    assert not os.path.exists("./upload/data/testfile.pdf")
