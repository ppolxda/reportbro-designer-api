# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 17:46:56.

@author: ppolxda

@desc: Error
"""


class ReportbroError(Exception):
    """ReportbroError."""


class StorageError(ReportbroError):
    """StorageError."""


class BackendError(ReportbroError):
    """BackendError."""


class TemplageNotFoundError(BackendError):
    """TemplageNotFoundError."""


class RetryError(ReportbroError):
    """RetryError."""


class NetConnectionError(ReportbroError):
    """NetConnectionError."""


class S3ClientError(ReportbroError):
    """S3ClientError."""


class ClientParamsError(ReportbroError):
    """ClientParamsError."""
