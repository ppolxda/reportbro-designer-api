# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 17:48:08.

@author: name

@desc: Base Model
"""
from typing import Any
from typing import Generic
from typing import List
from typing import Tuple
from typing import Type
from typing import TypeVar

import pydantic
from pydantic import ConfigDict
from pydantic import Field
from pydantic.alias_generators import to_camel

DataT = TypeVar("DataT")


class BaseModel(pydantic.BaseModel):
    """BaseModel."""

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class GenericModel(pydantic.BaseModel):
    """GenericModel."""

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class ErrorResponse(BaseModel):
    """Error Response."""

    code: int = Field(title="Error code")
    error: str = Field(title="Error message")


class DataResponse(ErrorResponse, GenericModel, Generic[DataT]):
    """Data Response."""

    data: DataT = Field(title="Data")

    @classmethod
    def __concrete_name__(cls: Type[Any], params: Tuple[Type[Any], ...]) -> str:
        """__concrete_name__."""
        return f"{params[0].__name__.title()}Response"


class ListResponse(ErrorResponse, GenericModel, Generic[DataT]):
    """List Response."""

    data: List[DataT] = Field(title="Data")

    @classmethod
    def __concrete_name__(cls: Type[Any], params: Tuple[Type[Any], ...]) -> str:
        """__concrete_name__."""
        return f"{params[0].__name__.title()}Response"
