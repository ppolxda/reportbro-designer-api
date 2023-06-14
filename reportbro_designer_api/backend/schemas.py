# -*- coding: utf-8 -*-
"""
@create: 2023-06-14 16:30:00.

@author: luofuwen

@desc: response
"""

from datetime import datetime

from humps import camelize
from pydantic import BaseModel as BaseModelSrc
from pydantic import Field


class BaseModel(BaseModelSrc):
    """BaseModel."""

    class Config:
        """Config."""

        orm_mode = True
        alias_generator = camelize
        allow_population_by_field_name = True
        # use_enum_values = True


class TemplatesIdInfo(BaseModel):
    """TemplatesId."""

    tid: str = Field("", title="tid")
    version_id: str = Field("", title="version_id")
    project: str = Field("", title="project")


class TemplateInfo(TemplatesIdInfo):
    """TemplateInfo."""

    # created_at: datetime = Field("", title="创建时间")
    updated_at: datetime = Field("", title="更新时间")
    template_name: str = Field("", title="模板名称")
    template_type: str = Field("", title="模板类型")


class TemplateConfigInfo(TemplateInfo):
    """TemplateConfigInfo."""

    report: dict = Field(default_factory=dict, title="模板配置")
