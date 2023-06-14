# -*- coding: utf-8 -*-
"""
@create: 2022-06-24 06:12:53.

@author: name

@desc: factory
"""
from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Optional
from uuid import uuid1

import shortuuid

from . import schemas as sa


class BackendBase(ABC):
    """BackendBase."""

    def gen_uuid(self) -> str:
        """Generate uuid."""
        return str(uuid1())

    def gen_uuid_short(self) -> str:
        """Generate uuid."""
        return str(shortuuid.encode(uuid1()))

    async def gen_uuid_object_key(
        self,
        project: Optional[str] = None,
    ) -> str:
        """Generate uuid."""
        _id = self.gen_uuid_short()
        tmpl = await self.is_template_exist(_id, project=project)
        if tmpl:
            rrr = await self.gen_uuid_object_key(project)
            return rrr
        return _id

    @abstractmethod
    async def clean_all(self):
        """Clean database, This api only use for test."""
        raise NotImplementedError

    @abstractmethod
    async def is_template_exist(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
    ) -> bool:
        """Is templates Exist."""
        raise NotImplementedError

    @abstractmethod
    async def get_templates_list(
        self,
        tid: Optional[str] = None,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
        template_name: Optional[str] = None,
        template_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[sa.TemplateInfo]:
        """Get templates list."""
        raise NotImplementedError

    async def get_templates_version_list(
        self,
        tid: str,
        project: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[sa.TemplateInfo]:
        """Get templates version list."""
        raise NotImplementedError

    @abstractmethod
    async def get_template(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
    ) -> Optional[sa.TemplateConfigInfo]:
        """Get templates."""
        raise NotImplementedError

    @abstractmethod
    async def put_template(
        self,
        template_name: str,
        template_type: str,
        report: dict,
        tid: Optional[str] = None,
        project: Optional[str] = None,
    ) -> sa.TemplatesIdInfo:
        """Put templates."""
        raise NotImplementedError

    @abstractmethod
    async def delete_template(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
    ):
        """Delete templates version."""
        raise NotImplementedError
