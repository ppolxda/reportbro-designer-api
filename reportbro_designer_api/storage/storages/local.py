# -*- coding: utf-8 -*-
"""
@create: 2023-06-21 20:59:09.

@author: ppolxda

@desc: S3 Storage
"""
import os
import shutil
import asyncio
from pathlib import Path
from typing import Optional
from fastapi import BackgroundTasks

# from reportbro_designer_api.errors import StorageError
from reportbro_designer_api.utils.logger import LOGGER

from .base import StorageBase


async def remove_files(storage_ttl: int, fs_path: Path):
    """RemoveFiles."""
    LOGGER.info("waiting remove file in %s", fs_path)
    await asyncio.sleep(storage_ttl)
    LOGGER.info("remove file in %s", fs_path)
    if fs_path.exists():
        os.remove(fs_path)


class LocalStorage(StorageBase):
    """S3Storage."""

    def __init__(
        self,
        storage_path: Optional[str] = None,
        storage_ttl: int = 30 * 60,
    ) -> None:
        """Init Local."""
        if not storage_path:
            storage_path = os.path.abspath(os.getcwd())
            storage_path = os.path.join(storage_path, "upload")

        self.storage_ttl = storage_ttl
        self.storage_path = Path(storage_path)
        self.thread = None
        # if not self.storage_path.is_dir():
        #     raise StorageError("storage_path is not dir")

        os.makedirs(storage_path, exist_ok=True)

    def auto_remove_file(self, fs_path: Path, background_tasks: BackgroundTasks):
        """Auto remove file."""
        LOGGER.info("add file in %s", fs_path)
        background_tasks.add_task(remove_files, self.storage_ttl, fs_path)

    async def clean_all(self):
        """Clean database, This api only use for test."""
        shutil.rmtree(self.storage_path)

    async def generate_presigned_url(self, s3_key: str) -> str:
        """Generate presigned url file, This api only use for test."""
        return s3_key

    async def put_file(
        self, s3_key: str, file_buffer: bytes, background_tasks: BackgroundTasks
    ):
        """Put file."""
        s3_obj = self.s3parse(s3_key)
        fpath = self.storage_path.joinpath(s3_obj.path[1:])

        os.makedirs(os.path.dirname(fpath), exist_ok=True)

        with open(fpath, "wb") as fs:
            fs.write(file_buffer)

        self.auto_remove_file(fpath, background_tasks)

    async def get_file(self, s3_key: str) -> Optional[bytes]:
        """Get file."""
        s3_obj = self.s3parse(s3_key)
        fpath = self.storage_path.joinpath(s3_obj.path[1:])

        if not fpath.exists():
            return None

        with open(fpath, "rb") as fs:
            return fs.read()
