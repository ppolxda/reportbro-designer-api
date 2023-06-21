# -*- coding: utf-8 -*-
"""
@create: 2023-06-21 20:59:09.

@author: ppolxda

@desc: S3 Storage
"""
import asyncio
import os
import shutil
from asyncio import AbstractEventLoop
from pathlib import Path
from typing import Optional

# from reportbro_designer_api.errors import StorageError
from reportbro_designer_api.utils.logger import LOGGER

from .base import StorageBase


def remove_files(fs_path: Path):
    """RemoveFiles."""
    LOGGER.info("remove file in %s", fs_path)
    if fs_path.exists():
        os.remove(fs_path)


class LocalStorage(StorageBase):
    """S3Storage."""

    def __init__(
        self,
        storage_path: Optional[str] = None,
        storage_ttl: int = 30 * 60,
        loop: Optional[AbstractEventLoop] = None,
    ) -> None:
        """Init Local."""
        if not storage_path:
            storage_path = os.path.abspath(os.getcwd())
            storage_path = os.path.join(storage_path, "upload")

        if not loop:
            loop = asyncio.get_event_loop()

        self.storage_ttl = storage_ttl
        self.storage_path = Path(storage_path)
        self.loop = loop
        # if not self.storage_path.is_dir():
        #     raise StorageError("storage_path is not dir")

        os.makedirs(storage_path, exist_ok=True)

    def auto_remove_file(self, fs_path: Path):
        """Auto remove file."""
        LOGGER.info("add file in %s", fs_path)
        self.loop.call_later(self.storage_ttl, remove_files, fs_path)

    async def clean_all(self):
        """Clean database, This api only use for test."""
        shutil.rmtree(self.storage_path)

    async def put_file(self, s3_key: str, file_buffer: bytes):
        """Put file."""
        s3_obj = self.s3parse(s3_key)
        fpath = self.storage_path.joinpath(s3_obj.path[1:])

        os.makedirs(os.path.dirname(fpath), exist_ok=True)

        with open(fpath, "wb") as fs:
            fs.write(file_buffer)

        self.auto_remove_file(fpath)

    async def get_file(self, s3_key: str) -> Optional[bytes]:
        """Get file."""
        s3_obj = self.s3parse(s3_key)
        fpath = self.storage_path.joinpath(s3_obj.path[1:])

        if not fpath.exists():
            return None

        with open(fpath, "rb") as fs:
            return fs.read()
