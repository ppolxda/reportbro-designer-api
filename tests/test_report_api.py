# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 18:42:56.

@author: ppolxda

@desc: test s3 client api
"""
import pytest

from reportbro_designer_api.settings import get_settings
from reportbro_designer_api.utils.report import ReportFontsLoader


@pytest.mark.usefixtures()
def test_fonts_api(debug_env):
    """Test reportbro fonts function."""
    settings = get_settings()

    fonts = ReportFontsLoader(settings.FONTS_PATH)
    assert len(fonts.fonts) == 4
