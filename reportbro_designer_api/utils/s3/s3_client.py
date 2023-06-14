# -*- coding: utf-8 -*-
"""
@create: 2023-06-13 11:00:00.

@author: luofuwen

@desc: s3 client
"""

from typing import Optional

from .base import S3Session


class S3Client(object):
    """文件管理服务."""

    def __init__(
        self,
        s3cli: S3Session,
        sign_expire: Optional[int] = None,
        bucket: Optional[str] = None,
    ):
        """初始化函数."""
        if bucket is None:
            bucket = ""
