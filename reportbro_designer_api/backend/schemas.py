# -*- coding: utf-8 -*-
"""
@create: 2023-06-14 16:30:00.

@author: luofuwen

@desc: response
"""

from datetime import datetime

from pydantic import Field

from reportbro_designer_api.utils.model import BaseModel


class BaseTemplate(BaseModel):
    """TemplateList."""

    template_name: str = Field(title="Template name")
    template_type: str = Field(title="Template type")


class BaseTemplateId(BaseModel):
    """TemplateList."""

    tid: str = Field(title="Template id")
    version_id: str = Field(title="Template version id")


class TemplateInfo(BaseTemplate, BaseTemplateId):
    """TemplateInfo."""

    # created_at: datetime = Field("", title="create at")
    updated_at: datetime = Field("", title="update at")


class TemplateConfigInfo(TemplateInfo):
    """TemplateConfigInfo."""

    report: dict = Field(default_factory=dict, title="Templage config")
