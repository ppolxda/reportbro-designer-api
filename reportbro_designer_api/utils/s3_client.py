# -*- coding: utf-8 -*-
"""
@create: 2023-06-13 11:00:00.

@author: luofuwen

@desc: s3 client
"""

from contextlib import asynccontextmanager
from typing import Optional

import aioboto3
from aiobotocore.config import AioConfig
from botocore.client import ClientError

from ..errors import S3ClientError


def hook_create_bucket_when_not_exist():
    """Create bucket when not exist."""

    def wrapper(func):
        async def wrapper_call(self, *args, **kwargs):
            await self.create_bucket_when_not_exist()
            return await func(self, *args, **kwargs)

        return wrapper_call

    return wrapper


def hook_object_not_exist():
    """Create bucket when not exist."""

    def wrapper(func):
        async def wrapper_call(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except ClientError as ex:
                if ex.response.get("Error", {}).get("Code", "") in ["404", "NoSuchKey"]:
                    return None

        return wrapper_call

    return wrapper


class S3ClientBase(object):
    """S3ClientBase."""

    TEMPLATES_PREFIX = "templates"
    REVIEW_PREFIX = "review"

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        endpoint_url: Optional[str] = None,
        region_name: str = "us-east-1",
        bucket: str = "reportbro",
    ):
        """Init s3."""
        self.region_name = region_name
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.config = AioConfig(signature_version="s3v4")
        self.bucket_name = bucket

    @asynccontextmanager
    async def s3cli(self):
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

    async def clear_bucket(self):
        """Clear bucket."""
        r = await self.__is_bucket_exist()
        if not r:
            await self.create_bucket_when_not_exist()
            return

        async with self.s3cli() as client:
            rrr = await client.list_object_versions(Bucket=self.bucket_name)
            if rrr.get("Versions", []):
                await client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={
                        "Objects": [
                            {"Key": i["Key"], "VersionId": i["VersionId"]}
                            for i in rrr.get("Versions", [])
                        ],
                    },
                )

            rrr = await client.list_objects_v2(Bucket=self.bucket_name)
            if rrr.get("Contents", []):
                await client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={
                        "Objects": [
                            {"Key": i["Key"], "VersionId": ""}
                            for i in rrr.get("Contents", [])
                        ],
                    },
                )
            await client.delete_bucket(Bucket=self.bucket_name)

    async def reset_bucket(self):
        """Delete bucket and Create bucket, Use for testing."""
        await self.clear_bucket()
        await self.create_bucket_when_not_exist()

    async def create_bucket_when_not_exist(self):
        """Create bucket when not exist."""
        if getattr(self, "has_bucket", False):
            return

        r = await self.__is_bucket_exist()
        if r:
            await self.__enable_bucket_versioning()
            await self.__enable_bucket_lifecycle()
            setattr(self, "has_bucket", True)
            return

        async with self.s3cli() as client:
            await client.create_bucket(Bucket=self.bucket_name, ACL="private")

        await self.__enable_bucket_versioning()
        await self.__enable_bucket_lifecycle()
        setattr(self, "has_bucket", True)

    async def __enable_bucket_lifecycle(self):
        """Enable bucket Lifecycle."""
        # TAG - https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutBucketLifecycleConfiguration.html#API_PutBucketLifecycleConfiguration_Examples
        res = await self.__is_bucket_lifecycle_exist()
        if res:
            return

        async with self.s3cli() as client:
            res = await client.put_bucket_lifecycle_configuration(
                Bucket=self.bucket_name,
                LifecycleConfiguration={
                    "Rules": [
                        {
                            "ID": "ReviewFileTemplate",
                            "Status": "Enabled",
                            "Prefix": self.REVIEW_PREFIX + "/",
                            "NoncurrentVersionExpiration": {
                                "NoncurrentDays": 1,
                                "NewerNoncurrentVersions": 5,
                            },
                        },
                    ]
                },
            )
            if res and res.get("ResponseMetadata", {}).get("HTTPStatusCode", 0) != 200:
                raise S3ClientError(f"Enabled Lifecycle Error[{res}]")

    async def __enable_bucket_versioning(self):
        """Enable bucket versioning."""
        if getattr(self, "has_bucket_versioning", False):
            return

        async with self.s3cli() as client:
            status = await client.get_bucket_versioning(Bucket=self.bucket_name)
            if status.get("Status", "") != "Enabled":
                res = await client.put_bucket_versioning(
                    Bucket=self.bucket_name,
                    VersioningConfiguration={
                        "MFADelete": "Disabled",
                        "Status": "Enabled",
                    },
                )
                if (
                    res
                    and res.get("ResponseMetadata", {}).get("HTTPStatusCode", 0) != 200
                ):
                    raise S3ClientError(f"Enabled BucketVersioning Error[{res}]")

            setattr(self, "has_bucket_versioning", True)

    async def __is_bucket_lifecycle_exist(self, bucket_name=None):
        """Is bucket exist."""
        if bucket_name is None:
            bucket_name = self.bucket_name

        async with self.s3cli() as client:
            try:
                # await client.head_bucket(Bucket=bucket_name)
                await client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            except ClientError as ex:
                if ex.response.get("Error", {}).get("Code", "") in [
                    "404",
                    "NoSuchLifecycleConfiguration",
                ]:
                    return False
                raise
            else:
                return True

    async def __is_bucket_exist(self, bucket_name: Optional[str] = None):
        """Is bucket exist."""
        if bucket_name is None:
            bucket_name = self.bucket_name

        async with self.s3cli() as client:
            try:
                await client.head_bucket(Bucket=bucket_name)
            except ClientError as ex:
                if ex.response.get("Error", {}).get("Code", "") == "404":
                    return False
                raise
            else:
                return True

    @hook_create_bucket_when_not_exist()
    async def _is_object_exist(self, object_key, version_id: Optional[str] = None):
        """Is bbject exist."""
        async with self.s3cli() as client:
            try:
                if version_id:
                    await client.head_object(
                        Bucket=self.bucket_name, Key=object_key, VersionId=version_id
                    )
                else:
                    await client.head_object(Bucket=self.bucket_name, Key=object_key)
            except ClientError as ex:
                if ex.response.get("Error", {}).get("Code", "") == "404":
                    return False
                raise
            else:
                return True
