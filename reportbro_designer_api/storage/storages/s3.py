# -*- coding: utf-8 -*-
"""
@create: 2023-06-21 20:59:09.

@author: ppolxda

@desc: S3 Storage
"""
from io import BytesIO
from typing import Optional

from filetype import guess

from reportbro_designer_api.utils.s3_client import S3ClientBase
from reportbro_designer_api.utils.s3_client import hook_create_bucket_when_not_exist
from reportbro_designer_api.utils.s3_client import hook_object_not_exist

from ...errors import StorageError
from .base import StorageBase


class S3Storage(S3ClientBase, StorageBase):
    """S3Storage."""

    async def clean_all(self):
        """Clean database, This api only use for test."""
        await self.clear_bucket()

    @hook_create_bucket_when_not_exist()
    async def put_file(self, s3_key: str, file_buffer: bytes):
        """Put file."""
        s3_obj = self.s3parse(s3_key)
        content = guess(file_buffer)
        if not content:
            raise StorageError("filetype support")

        content = content.mime

        async with self.s3cli() as client:
            res = await client.put_object(
                Bucket=self.bucket_name,
                Key=s3_obj.path,
                Body=BytesIO(file_buffer),
                ContentType=content,
            )
            if res.get("ResponseMetadata", {}).get("HTTPStatusCode", "") != 200:
                raise StorageError(f"Save file error[{res}]")

    @hook_create_bucket_when_not_exist()
    @hook_object_not_exist()
    async def get_file(self, s3_key: str) -> Optional[bytes]:
        """Get file."""
        s3_obj = self.s3parse(s3_key)
        async with self.s3cli() as client:
            res = await client.get_object(Bucket=self.bucket_name, Key=s3_obj.path)
            data = await res["Body"].read()
            return data
