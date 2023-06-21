# -*- coding: utf-8 -*-
"""
@create: 2023-06-21 21:52:07.

@author: ppolxda

@desc: Storage manage
"""
import base64
import os
from typing import Optional
from typing import Tuple

from ..errors import StorageError
from .storages.base import StorageBase

DowmloadKey = str
FileName = str


class StorageMange(object):
    """类功能描述.

    具体字段描述
    """

    REVIEW_PREFIX = "review"

    def __init__(
        self,
        storage: StorageBase,
        project: str = "default",
    ):
        """初始化函数."""
        self.storage = storage
        self.project_name = project

    def make_s3_key(self, filename, project: Optional[str] = None):
        """Make review key."""
        if not project:
            project = self.project_name

        return "s3://" + "/".join([self.REVIEW_PREFIX, project, filename])

    async def put_file(
        self, filename: str, file_buffer: bytes, project: Optional[str] = None
    ) -> DowmloadKey:
        """Put file."""
        project = project if project else self.project_name
        s3_key = self.make_s3_key(filename, project)
        await self.storage.put_file(s3_key, file_buffer)
        return "key:" + base64.b64encode(s3_key.encode("utf8")).decode("utf8")

    async def get_file(self, download_key: DowmloadKey) -> Tuple[FileName, bytes]:
        """Get file."""
        if download_key.startswith("key:"):
            # raise StorageError(f"download_key invaild[{download_key}]")
            download_key = download_key[4:]

        s3_key = base64.b64decode(download_key.encode("utf8")).decode("utf8")
        r = await self.storage.get_file(s3_key)
        if not r:
            raise StorageError(f"download_key not exist[{download_key}]")

        return os.path.dirname(s3_key), r
