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
from humps.main import camelize
from pydantic import Field
from pydantic import generics

DataT = TypeVar("DataT")


class BaseModel(pydantic.BaseModel):
    """BaseModel."""

    class Config:
        """Config."""

        orm_mode = True
        alias_generator = camelize
        allow_population_by_field_name = True
        # use_enum_values = True


class GenericModel(generics.GenericModel):
    """GenericModel."""

    class Config:
        """Config."""

        orm_mode = True
        alias_generator = camelize
        allow_population_by_field_name = True
        # use_enum_values = True


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
