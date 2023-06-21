# -*- coding: utf-8 -*-
"""
@create: 2023-06-19 16:40:52.

@author: luofuwen

@desc: response
"""
from pydantic import BaseModel
from pydantic import Field


class PdfStorageKey(BaseModel):
    """ReviewResponse."""

    object_key: str = Field("", title="object_key")
    version_id: str = Field("", title="version_id")


class PdfStorageData(PdfStorageKey):
    """ReviewResponse."""

    filename: str = Field("", title="filename")
    data: bytes = Field(b"", title="data")
