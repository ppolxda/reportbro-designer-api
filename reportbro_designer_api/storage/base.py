# -*- coding: utf-8 -*-
"""
@create: 2023-06-14 17:30:00.

@author: luofuwen

@desc: Base
"""


from abc import ABC
from abc import abstractmethod

from ..backend import reportbro_schemas as sa


class StorageBase(ABC):
    """StorageBase."""

    @abstractmethod
    def put_review(
        self,
        file_surfix: str,
        file_buffer: bytes,
        filename: str,
        project: Optional[str] = None,
    ) -> sa.ReviewResponse:
        """Put templates."""
        raise NotImplementedError

    @abstractmethod
    def get_review(
        self, file_surfix: str, version_id: str, project: Optional[str] = None
    ) -> sa.ReviewDataResponse:
        """Get templates."""
        raise NotImplementedError
