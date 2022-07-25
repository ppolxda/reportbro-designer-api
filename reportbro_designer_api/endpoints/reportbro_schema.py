# -*- coding: utf-8 -*-
"""
@create: 2022-07-25 10:39:19.

@author: ppolxda

@desc: ReportBro Api
"""
from typing import Optional

from pydantic import Field

from reportbro_designer_api.utils.model import BaseModel
from reportbro_designer_api.utils.model import DataResponse
from reportbro_designer_api.utils.model import ListResponse


class BaseTemplate(BaseModel):
    """TemplateList."""

    template_name: str = Field(title="Template name")
    template_type: str = Field(title="Template type")


class TemplateListData(BaseTemplate):
    """TemplateList."""

    tid: str = Field(title="Template id")
    version_id: str = Field(title="Template version id")


class TemplateDescData(BaseTemplate):
    """TemplateList."""

    tid: str = Field(title="Template id")
    version_id: str = Field(title="Template version id")
    report: dict = Field(title="Template Data")


class RequestCreateTemplate(BaseTemplate):
    """RequestCreateTemplate."""


class RequestUploadTemplate(BaseModel):
    """RequestUploadTemplate."""

    report: dict = Field(title="Template Data")


class RequestGenerateTemplate(BaseModel):
    """RequestGenerateTemplate."""

    output_format: str = Field(
        "pdf", title="Output Format(pdf|xlsx)", regex=r"^(pdf|xlsx)$"
    )
    data: dict = Field(title="Source Data")


class RequestReviewTemplate(RequestGenerateTemplate):
    """RequestReviewTemplate."""

    report: dict = Field(title="Template Data")
    is_test_data: bool = Field(title="Is test data")


class RequestCloneTemplate(BaseModel):
    """RequestCloneTemplate."""

    from_tid: str = Field(title="Clone from template id")
    from_version_id: Optional[str] = Field(None, title="Clone from Template version id")


class TemplateListResponse(ListResponse[TemplateListData]):
    """TemplateListResponse."""


class TemplateDescResponse(DataResponse[TemplateDescData]):
    """TemplateDescResponse."""


class TemplateDataResponse(DataResponse[TemplateListData]):
    """TemplateDataResponse."""
