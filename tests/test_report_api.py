# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 18:42:56.

@author: ppolxda

@desc: test s3 client api
"""
import json
import os

import pytest

from reportbro_designer_api.settings import get_settings
from reportbro_designer_api.utils.report import ReportFontsLoader
from reportbro_designer_api.utils.report import fill_default

FPATH = os.path.abspath(os.path.dirname(__file__))


@pytest.mark.usefixtures()
def test_fonts_api(debug_env):
    """Test reportbro fonts function."""
    assert debug_env is None
    settings = get_settings()
    fonts = ReportFontsLoader(settings.FONTS_PATH)
    assert len(fonts.fonts) == 4


@pytest.mark.usefixtures()
def test_padding_data(debug_env):
    """Test reportbro padding function."""
    assert debug_env is None
    data_path = FPATH + "/data/padding_template.json"
    with open(data_path, "r", encoding="utf8") as fss:
        data_json = json.loads(fss.read())

    data = {}
    fill_default(data_json, data)
    assert "page_count" not in data
    assert "page_number" not in data
    assert data["bool_value"] is False
    assert data["string_value"] == ""
    assert data["number_value"] == 0
    assert data["date_value"] == "1900-01-01"
    assert data["image_value"] == ""
    assert data["slist_value"] == []
    assert data["nlist_value"] == []
    assert data["list_value"] == []
    assert data["group_value"] == {
        "gstring_value": "",
        "gnumber_value": 0,
    }
    assert "sum_value" not in data
    assert "avg_value" not in data

    data = {
        "nlist_value": [1, 2],
        "list_value": [
            {
                "lstring_value": "111",
            }
        ],
        "group_value": {
            "gstring_value": "",
            "gnumber_value": 1,
        },
    }
    fill_default(data_json, data)
    assert data["slist_value"] == []
    assert data["nlist_value"] == [1, 2]
    assert data["list_value"] == [
        {
            "lnumber_value": 0.0,
            "lstring_value": "111",
        }
    ]
    assert data["group_value"] == {
        "gstring_value": "",
        "gnumber_value": 1,
    }
