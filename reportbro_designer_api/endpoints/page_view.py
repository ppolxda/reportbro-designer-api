# -*- coding: utf-8 -*-
"""
@create: 2022-07-25 10:39:05.

@author: ppolxda

@desc: page_view
"""
import json
from enum import Enum
from gettext import NullTranslations
from typing import List
from typing import Optional
from typing import Union

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import Query
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from reportbro_designer_api.settings import settings

from ..backend.base import BackendBase
from ..clients import FONTS_LOADER
from ..clients import get_meth_cli
from ..errors import TemplageNotFoundError

router = APIRouter()
TAGS: List[Union[str, Enum]] = ["Static Page"]
templates = Jinja2Templates(
    directory=settings.TEMPLATES_PATH, extensions=["jinja2.ext.i18n"]
)

translation = NullTranslations()
templates.env.install_gettext_translations(translation)  # pylint: disable=no-member


@router.get("/", tags=TAGS, name="Main page")
async def main_index_page():
    """Web main page."""
    return RedirectResponse("/templates")


@router.get("/templates", tags=TAGS, name="Templates Manage page")
async def templates_index_page():
    """Templates Manage page."""
    return RedirectResponse("/templates")


@router.get("/designer/{tid}", tags=TAGS, name="Templates Designer page")
async def templates_designer_page(
    request: Request,
    tid: str = Path(title="Template id"),
    version_id: Optional[str] = Query(None, title="Template version id"),
    menu_show_debug: bool = Query(True, title="Show Menu Debug", alias="menuShowDebug"),
    menu_sidebar: bool = Query(False, title="Show Menu Sidebar", alias="menuSidebar"),
    locale: str = Query(
        settings.PDF_LOCALE,
        title="Show Menu Language(zh_cn|de_de|en_us)",
        alias="locale",
        regex=r"^(zh_cn|de_de|en_us)$",
    ),
    client: BackendBase = Depends(get_meth_cli),
):
    """Templates Designer page."""
    obj = await client.get_template(tid, version_id)
    if not obj:
        raise TemplageNotFoundError("template not found")

    version_id = obj.version_id
    return templates.TemplateResponse(
        "designer.html.jinja2",
        {
            "request": request,
            "tid": tid,
            "version_id": version_id,
            "report": json.dumps(obj.report, indent=2),
            "fonts": FONTS_LOADER.fonts_jinja,
            "default_font": settings.PDF_DEFAULT_FONT,
            "menu_sidebar": menu_sidebar,
            "menu_show_debug": menu_show_debug,
            "locale": locale,
        },
    )
