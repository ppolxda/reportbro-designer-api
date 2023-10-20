# -*- coding: utf-8 -*-
"""
@create: 2023-10-20 16:12:12.

@author: ppolxda

@desc: main_page_view
"""
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/", name="Main page")
async def main_index_page():
    """Web main page."""
    return RedirectResponse("/ui")
