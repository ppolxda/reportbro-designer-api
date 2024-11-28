# -*- coding: utf-8 -*-
"""
@create: 2024-11-25 23:40:15.

@author: ppolxda

@desc: test web api
"""

import json
import os

import filetype
import pytest
from fastapi.testclient import TestClient

from reportbro_designer_api.backend import S3Backend
from reportbro_designer_api.endpoints import reportbro_schema as ss
from reportbro_designer_api.main import app
from reportbro_designer_api.storage import S3Storage

client = TestClient(app)
FPATH = os.path.abspath(os.path.dirname(__file__))


def is_pdf(data: bytes):
    """is_pdf."""
    rtype = filetype.guess(data)
    return rtype and rtype.extension == "pdf"


def web_generate_pdf_review():
    """Test web api generate pdf review."""
    out_path = FPATH + "/../out"
    data_path = FPATH + "/data/checkbox_template.json"
    with open(data_path, "r", encoding="utf8") as fss:
        data_json = json.loads(fss.read())

    response = client.put(
        "/api/templates/review/generate",
        json=ss.RequestReviewTemplate(
            output_format="pdf",
            data=data_json["data"],
            report=data_json["report"],
            is_test_data=False,
        ).model_dump(),
    )
    assert (
        response.status_code == 200
        and response.text
        and response.text.startswith("key:")
    ), response.text

    filekey = response.text
    response = client.get(
        "/api/templates/review/generate",
        params={
            "outputFormat": "pdf",
            "key": filekey,
        },
    )
    assert is_pdf(response.content)
    with open(out_path + "/review_test_checkbox.pdf", "wb") as fss:
        fss.write(response.content)


@pytest.mark.asyncio
async def test_s3_pdf_checkbox_generate(s3cli: S3Backend, s3storage: S3Storage):
    """Test s3 reportbro api function."""
    assert s3cli
    web_generate_pdf_review()
