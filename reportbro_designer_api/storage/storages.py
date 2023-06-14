# -*- coding: utf-8 -*-
"""
@create: 2023-06-14 17:30:00.

@author: luofuwen

@desc: Local Storage
"""

import asyncio
import os
from io import BytesIO
from typing import Optional

from ..backend import schemas as sa
from ..backend.s3 import S3Backend
from ..errors import ClientParamsError
from ..errors import S3ClientError
from .base import StorageBase


class StorageCommonBase(object):
    """StorageBase."""

    def judge_type(self, file_surfix: str) -> str:
        """判断文件类型."""
        if file_surfix == "pdf":
            ctx = "application/pdf"
        elif file_surfix == "xlsx":
            ctx = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            raise ClientParamsError(f"file_surfix invaild[{file_surfix}]")
        return ctx


class LocalStorage(StorageCommonBase, StorageBase):
    """LocalStorage."""

    def __init__(self, storage_path: Optional[str] = None) -> None:
        """初始化函数."""
        if not storage_path:
            storage_path = os.path.abspath(os.path.dirname(__file__))

        self.storage_path = storage_path

    def upload_files(self, file_name: str, file_buffer: bytes):
        """UploadFiles."""
        path_ = os.path.join(self.storage_path)

        if not os.path.exists(path_):
            os.mkdir(path_)

        with open(os.path.join(path_, file_name), "wb") as fff:
            fff.write(file_buffer)

        # 回调函数
        def _loop_call_later(path_: str, delay=30 * 60):
            loop = asyncio.get_event_loop()
            loop.call_later(delay, self.remove_files, path_)

        _loop_call_later(os.path.join(path_, file_name))

    def down_files(self, file_name: str) -> bytes:
        """DownFiles."""
        path_ = os.path.join(self.storage_path, file_name)

        if not os.path.exists(path_):
            return b""

        with open(path_, "rb") as fff:
            return fff.read()

    def remove_files(self, file_name: str):
        """RemoveFiles."""
        path_ = os.path.join(self.storage_path, file_name)
        if os.path.exists(path_):
            os.remove(path_)

    def put_review(
        self,
        file_surfix: str,
        file_buffer: bytes,
        filename: str,
        project: Optional[str] = None,
    ) -> sa.ReviewResponse:
        """Put templates."""
        self.judge_type(file_surfix)
        self.upload_files(filename, file_buffer)
        key = filename
        return sa.ReviewResponse(object_key="", version_id=key)

    def get_review(
        self, file_surfix: str, version_id: str, project: Optional[str] = None
    ) -> sa.ReviewDataResponse:
        """Get templates."""
        filename = version_id
        data = self.down_files(filename)
        return sa.ReviewDataResponse(object_key="", filename=filename, data=data)


class S3Storage(StorageCommonBase, StorageBase, S3Backend):
    """S3Storage."""

    TEMPLATES_PREFIX = "templates"
    REVIEW_PREFIX = "review"

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        endpoint_url: Optional[str] = None,
        region_name: str = "us-east-1",
        bucket: str = "reportbro",
        project: str = "default",
        default_template: Optional[dict] = None,
    ):
        """init."""
        super().__init__(
            aws_access_key_id,
            aws_secret_access_key,
            endpoint_url,
            region_name,
            bucket,
            project,
            default_template,
        )

    def put_review(
        self,
        file_surfix: str,
        file_buffer: bytes,
        filename: str,
        project: Optional[str] = None,
    ) -> sa.ReviewResponse:
        """Put templates."""
        ctx = self.judge_type(file_surfix)
        object_key = self.make_review_key(file_surfix, project)
        res = self.bucket.Object(object_key).put(
            Body=BytesIO(file_buffer),
            ContentType=ctx,
            Metadata=self.encode_matedata(
                {
                    "filename": filename,
                }
            ),
        )
        if res.get("ResponseMetadata", {}).get("HTTPStatusCode", "") != 200:
            raise S3ClientError(f"Save Template File Error[{res}]")

        return sa.ReviewResponse(object_key=object_key, version_id=res["VersionId"])

    def get_review(
        self, file_surfix: str, version_id: str, project: Optional[str] = None
    ) -> sa.ReviewDataResponse:
        """Get templates."""
        self.create_bucket_when_not_exist()
        object_key = self.make_review_key(file_surfix, project)
        obj = self.bucket.Object(object_key)
        res = obj.get(VersionId=version_id)

        if res.get("ResponseMetadata", {}).get("HTTPStatusCode", "") != 200:
            raise S3ClientError(f"Save Template File Error[{res}]")

        mdata = self.decode_matedata(res["Metadata"])
        return sa.ReviewDataResponse(
            object_key=object_key, filename=mdata["filename"], data=res["Body"].read()
        )
