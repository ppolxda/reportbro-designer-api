# -*- coding: utf-8 -*-
"""
@create: 2023-06-21 20:23:25.

@author: ppolxda

@desc: Backend
"""
from .mange import StorageMange
from .storages.base import StorageBase
from .storages.local import LocalStorage
from .storages.s3 import S3Storage

__all__ = [
    "StorageBase",
    "S3Storage",
    "LocalStorage",
    "StorageMange",
]
