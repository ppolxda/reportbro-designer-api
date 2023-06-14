# -*- coding: utf-8 -*-
"""
@create: 2023-06-19 16:06:57.

@author: ppolxda

@desc: model define
"""
from datetime import datetime

from sqlalchemy import JSON
from sqlalchemy import TIMESTAMP
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

# pylint: disable=line-too-long


def local_now():
    """Make now."""
    return datetime.now()


class Base(AsyncAttrs, DeclarativeBase):
    """Models Base."""

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime, default=local_now, nullable=False)  # type: ignore
    updated_at: Mapped[datetime] = mapped_column("updated_at", TIMESTAMP, default=local_now, nullable=False, onupdate=local_now)  # type: ignore


class TemplatesVersion(Base):
    """Templates Table."""

    __tablename__ = "templates_version"

    tid: Mapped[str] = mapped_column(String(50), default=str, nullable=False, primary_key=True)  # type: ignore
    version_id: Mapped[str] = mapped_column(String(50), default=str, nullable=False, primary_key=True)  # type: ignore
    project: Mapped[str] = mapped_column(String(30), default=str, nullable=False, primary_key=True)  # type: ignore
    template_name: Mapped[str] = mapped_column(String(30), default=str, nullable=False)  # type: ignore
    template_type: Mapped[str] = mapped_column(String(30), default=str, nullable=False)  # type: ignore
    template_config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # type: ignore


class Templates(Base):
    """Templates Table."""

    __tablename__ = "templates"

    tid: Mapped[str] = mapped_column(String(50), default=str, nullable=False, primary_key=True)  # type: ignore
    project: Mapped[str] = mapped_column(String(30), default=str, nullable=False, primary_key=True)  # type: ignore
    version_id: Mapped[str] = mapped_column(String(50), default=str, nullable=False)  # type: ignore
    template_name: Mapped[str] = mapped_column(String(30), default=str, nullable=False)  # type: ignore
    template_type: Mapped[str] = mapped_column(String(30), default=str, nullable=False)  # type: ignore
    template_config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # type: ignore
