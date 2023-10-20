# -*- coding: utf-8 -*-
"""
@create: 2023-06-21 20:13:15.

@author: ppolxda

@desc: File Storage
"""
from abc import ABC
from abc import abstractmethod
from typing import Optional
from urllib.parse import urlparse
from fastapi import BackgroundTasks

from ...errors import StorageError


class StorageBase(ABC):
    """StorageBase."""

    @staticmethod
    def s3parse(s3_key: str):
        """s3parse."""
        s3_parse = urlparse(s3_key)
        if not s3_parse.scheme.startswith("s3"):
            raise StorageError(f"s3_key invaild[{s3_key}]")
        if not s3_parse.path.startswith("/"):
            raise StorageError(f"s3_key invaild[{s3_key}]")
        return s3_parse

    @abstractmethod
    async def clean_all(self):
        """Clean database, This api only use for test."""
        raise NotImplementedError

    @abstractmethod
    async def generate_presigned_url(self, s3_key: str) -> str:
        """Generate presigned url file, This api only use for test."""

    @abstractmethod
    async def put_file(
        self, s3_key: str, file_buffer: bytes, background_tasks: BackgroundTasks
    ):
        """Put file."""
        raise NotImplementedError

    @abstractmethod
    async def get_file(self, s3_key: str) -> Optional[bytes]:
        """Get file."""
        raise NotImplementedError
