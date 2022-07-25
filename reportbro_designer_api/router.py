# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 17:44:59.

@author: ppolxda

@desc: router
"""
from fastapi import APIRouter

from .endpoints.page_view import router as view_router
from .endpoints.reportbro_api import router as reportbro_router

router = APIRouter()
router.include_router(reportbro_router, prefix="/api")
router.include_router(view_router, prefix="/view")
