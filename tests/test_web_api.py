# -*- coding: utf-8 -*-
"""
@create: 2022-07-29 15:18:16.

@author: ppolxda

@desc: test web api
"""
import json
import os
from copy import deepcopy

import filetype
import pytest
from fastapi.testclient import TestClient

from reportbro_designer_api.errors import S3ClientError
from reportbro_designer_api.main import app
from reportbro_designer_api.utils.s3 import ReportbroS3Client

client = TestClient(app)
FPATH = os.path.abspath(os.path.dirname(__file__))


def is_pdf(data: bytes):
    """is_pdf."""
    rtype = filetype.guess(data)
    return rtype and rtype.extension == "pdf"


@pytest.fixture(name="default_template")
def fixture_default_template(s3cli: ReportbroS3Client):
    """default_template."""
    assert s3cli
    # check s3 empty
    response = client.get("/api/templates/list")
    assert response.status_code == 200
    assert response.json() == {"code": 200, "error": "ok", "data": []}

    # create templates
    response = client.put(
        "/api/templates", json={"templateName": "test", "templateType": "test"}
    )
    assert response.status_code == 200
    rdata = response.json()
    tid = rdata["data"]["tid"]
    version_id = rdata["data"]["versionId"]
    assert tid and version_id
    assert "/" not in tid
    assert rdata["data"]["templateName"] == "test"
    assert rdata["data"]["templateType"] == "test"

    # get templates desc
    response = client.get(
        f"/api/templates/{tid}/desc",
        params={"versionId": version_id},
    )
    assert response.status_code == 200
    tempdata = response.json()
    assert "/" not in tempdata["data"]["tid"]
    assert tempdata["data"]["report"]
    assert tempdata["data"]["templateName"] == "test"
    assert tempdata["data"]["templateType"] == "test"
    return tempdata["data"]


def test_web_api(default_template):
    """Test web api."""
    assert default_template and isinstance(default_template, dict)
    tempdata = default_template
    report = tempdata["report"]
    tid = tempdata["tid"]
    version_id = tempdata["versionId"]

    # check s3 list tid
    response = client.get("/api/templates/list")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert "/" not in response.json()["data"][0]["tid"]

    # create templates test1
    response = client.put(
        "/api/templates", json={"templateName": "test1", "templateType": "test1"}
    )
    assert response.status_code == 200
    rdata1 = response.json()
    tid1 = rdata1["data"]["tid"]
    version_id1 = rdata1["data"]["versionId"]
    assert tid1 and version_id1
    assert "/" not in tid1
    assert rdata1["data"]["templateName"] == "test1"
    assert rdata1["data"]["templateType"] == "test1"

    # get templates desc test1
    response = client.get(
        f"/api/templates/{tid1}/desc",
        params={"versionId": version_id1},
    )
    assert response.status_code == 200
    tempdata = response.json()
    assert "/" not in tempdata["data"]["tid"]
    assert tempdata["data"]["report"]
    assert tempdata["data"]["templateName"] == "test1"
    assert tempdata["data"]["templateType"] == "test1"

    # check s3 list version
    response = client.get(f"/api/templates/{tid}/versions")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert "/" not in response.json()["data"][0]["tid"]

    # check s3 list
    response = client.get("/api/templates/list")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert "/" not in response.json()["data"][0]["tid"]

    # modify templates test1
    report2 = deepcopy(report)
    report2["version"] = 2
    response = client.post(
        f"/api/templates/{tid}",
        json={"report": report2},
    )
    assert response.status_code == 200
    rdata3 = response.json()
    assert rdata3["data"]["templateName"] == "test"
    assert rdata3["data"]["templateType"] == "test"
    assert rdata3["data"]["tid"] == tid
    assert rdata3["data"]["versionId"] != version_id

    # get templates desc version
    response = client.get(f"/api/templates/{tid}/desc")
    assert response.status_code == 200
    tempdata = response.json()
    assert tempdata["data"]["versionId"] == rdata3["data"]["versionId"]
    assert tempdata["data"]["report"]["version"] == report2["version"]

    # create templates test1
    response = client.post(
        f"/api/templates/{tid}/clone",
        json={"fromTid": tid1, "fromVersionId": version_id1},
    )
    assert response.status_code == 200
    rdata = response.json()
    assert rdata["data"]["versionId"] != tempdata["data"]["versionId"]
    assert rdata["data"]["templateName"] == "test"
    assert rdata["data"]["templateType"] == "test"

    # get templates desc version
    response = client.get(f"/api/templates/{tid}/desc")
    assert response.status_code == 200
    tempdata = response.json()
    assert tempdata["data"]["versionId"] == rdata["data"]["versionId"]
    assert tempdata["data"]["report"]["version"] == 1

    # check s3 list version
    response = client.get(f"/api/templates/{tid}/versions")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 3
    assert "/" not in response.json()["data"][0]["tid"]


def test_web_generate_pdf_review(default_template):
    """Test web api generate pdf review."""
    assert default_template and isinstance(default_template, dict)
    tempdata = default_template
    report = tempdata["report"]
    tid = tempdata["tid"]
    # version_id = tempdata["versionId"]

    out_path = FPATH + "/../out"
    data_path = FPATH + "/data/default_template_data.json"
    with open(data_path, "r", encoding="utf8") as fss:
        data_json = json.loads(fss.read())

    response = client.put(
        "/api/templates/review",
        json={
            "outputFormat": "pdf",
            "data": data_json,
            "report": report,
            "isTestData": True,
        },
    )
    assert (
        response.status_code == 200
        and response.text
        and response.text.startswith("key:")
    )
    filekey = response.text
    response = client.get(
        "/api/templates/review",
        params={
            "outputFormat": "pdf",
            "key": filekey,
        },
    )
    assert is_pdf(response.content)
    with open(out_path + "/review_test_data.pdf", "wb") as fss:
        fss.write(response.content)

    response = client.put(
        "/api/templates/review",
        json={
            "outputFormat": "pdf",
            "data": data_json,
            "report": report,
            "isTestData": False,
        },
    )
    assert (
        response.status_code == 200
        and response.text
        and response.text.startswith("key:")
    )
    filekey = response.text
    response = client.get(
        "/api/templates/review",
        params={
            "outputFormat": "pdf",
            "key": filekey,
        },
    )
    assert is_pdf(response.content)
    with open(out_path + "/review_data.pdf", "wb") as fss:
        fss.write(response.content)

    # test gen by id
    response = client.put(
        f"/api/templates/{tid}/generate",
        json={
            "outputFormat": "pdf",
            "data": data_json,
        },
    )
    assert (
        response.status_code == 200
        and response.text
        and response.json()["data"]["downloadKey"].startswith("key:")
        and response.json()["data"]["downloadUrl"]
    )
    download_url = response.json()["data"]["downloadUrl"]
    filekey = response.json()["data"]["downloadKey"]
    response = client.get(
        f"/api/templates/{tid}/generate",
        params={
            "outputFormat": "pdf",
            "key": filekey,
        },
    )
    assert is_pdf(response.content)
    with open(out_path + "/generate_data.pdf", "wb") as fss:
        fss.write(response.content)

    response = client.get(download_url)
    assert is_pdf(response.content)
    with open(out_path + "/generate_data_url.pdf", "wb") as fss:
        fss.write(response.content)


def test_web_generate_pdf_mutil(default_template, s3cli: ReportbroS3Client):
    """Test web api generate pdf."""
    assert default_template and isinstance(default_template, dict)
    tempdata = default_template
    # report = tempdata["report"]
    tid = tempdata["tid"]
    version_id = tempdata["versionId"]

    out_path = FPATH + "/../out"
    testfile_path = FPATH + "/data/testfile.pdf"
    data_path = FPATH + "/data/default_template_data.json"
    with open(data_path, "r", encoding="utf8") as fss:
        data_json = json.loads(fss.read())

    object_key = "testfile.pdf"
    obj = s3cli.bucket.Object(object_key)
    with open(testfile_path, "rb") as ffs:
        res = obj.put(
            Body=ffs,
            ContentType="application/pdf",
        )
        if res.get("ResponseMetadata", {}).get("HTTPStatusCode", "") != 200:
            raise S3ClientError(f"Save Template File Error[{res}]")

    testfile_url = s3cli.s3cli.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": s3cli.bucket_name, "Key": object_key},
        ExpiresIn=3600,
    )

    # test gen mutil
    response = client.put(
        "/api/templates/multi/generate",
        json={
            "outputFormat": "pdf",
            "templates": [
                {
                    "tid": tid,
                    "versionId": version_id,
                    "data": data_json,
                },
                {
                    "tid": tid,
                    "versionId": version_id,
                    "data": data_json,
                },
            ],
        },
    )
    assert (
        response.status_code == 200
        and response.text
        and response.json()["data"]["downloadKey"].startswith("key:")
        and response.json()["data"]["downloadUrl"]
    )
    download_url = response.json()["data"]["downloadUrl"]
    filekey = response.json()["data"]["downloadKey"]
    response = client.get(
        "/api/templates/multi/generate",
        params={
            "outputFormat": "pdf",
            "key": filekey,
        },
    )
    assert is_pdf(response.content)
    multi_data_path = out_path + "/multi_data.pdf"
    with open(out_path + "/multi_data.pdf", "wb") as fss:
        fss.write(response.content)

    response = client.get(download_url)
    assert is_pdf(response.content)
    with open(out_path + "/multi_data_url.pdf", "wb") as fss:
        fss.write(response.content)

    # test gen mutil
    response = client.put(
        "/api/templates/multi/generate",
        json={
            "outputFormat": "pdf",
            "templates": [
                {
                    "tid": tid,
                    "versionId": version_id,
                    "data": data_json,
                },
                {
                    "pdfUrl": "file://" + multi_data_path,
                },
                {
                    "pdfUrl": testfile_url,
                },
                {
                    "tid": tid,
                    "versionId": version_id,
                    "data": data_json,
                },
            ],
        },
    )
    assert (
        response.status_code == 200
        and response.text
        and response.json()["data"]["downloadKey"].startswith("key:")
        and response.json()["data"]["downloadUrl"]
    )
    download_url = response.json()["data"]["downloadUrl"]
    filekey = response.json()["data"]["downloadKey"]
    response = client.get(
        "/api/templates/multi/generate",
        params={
            "outputFormat": "pdf",
            "key": filekey,
        },
    )
    assert is_pdf(response.content)
    with open(out_path + "/multi_download_data.pdf", "wb") as fss:
        fss.write(response.content)

    response = client.get(download_url)
    assert is_pdf(response.content)
    with open(out_path + "/multi_data_url.pdf", "wb") as fss:
        fss.write(response.content)


def test_web_api_non_ascii(s3cli: ReportbroS3Client):
    """Test web api."""
    assert s3cli

    # create templates test1
    response = client.put(
        "/api/templates", json={"templateName": "测试", "templateType": "测试"}
    )
    assert response.status_code == 200
    rdata1 = response.json()
    tid1 = rdata1["data"]["tid"]
    version_id1 = rdata1["data"]["versionId"]
    assert tid1 and version_id1
    assert "/" not in tid1
    assert rdata1["data"]["templateName"] == "测试"
    assert rdata1["data"]["templateType"] == "测试"
