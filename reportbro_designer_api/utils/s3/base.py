# -*- coding: utf-8 -*-
"""
@create: 2023-06-13 10:40:00.

@author: luofuwen

@desc: s3 geet session client
"""
import contextlib
from typing import Optional

import aioboto3
from aiobotocore.config import AioConfig
from botocore.exceptions import ClientError


class S3Session:
    """S3Session."""

    def __init__(
        self,
        endpoint_url,
        aws_access_key_id,
        aws_secret_access_key,
        region_name="us-east-1",
    ) -> None:
        """初始化函数."""
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.config = AioConfig(signature_version="s3v4")

    @contextlib.asynccontextmanager
    async def client(self):
        """创建客户端."""
        session = aioboto3.Session()
        async with session.client(
            "s3",
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            config=self.config,
        ) as s3cli:
            yield s3cli


class S3Client(object):
    """文件管理服务."""

    def __init__(
        self,
        client: S3Session,
        bucket: Optional[str] = None,
    ):
        """初始化函数."""
        if bucket is None:
            bucket = "test_bucket_create"

        self.client = client
        self.bucket = bucket

    async def create_bucket_when_not_exists(self, bucket: str):
        """如果桶不存在创建桶."""
        async with self.client.client() as s3cli:
            try:
                await s3cli.head_bucket(Bucket=bucket)
            except ClientError as ex:
                assert isinstance(ex.response, dict)
                if ex.response.get("Error", {}).get("Code", "") in [
                    "NoSuchKey",
                ] or ex.response.get("Error", {}).get("Message", "") in [
                    "Not Found",
                ]:
                    await s3cli.create_bucket(Bucket=bucket)
                    return True
                raise ex
            return False
