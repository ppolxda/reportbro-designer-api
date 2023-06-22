# -*- coding: utf-8 -*-
"""
@create: 2022-07-29 15:18:16.

@author: ppolxda

@desc: test web api
"""
import json
import os
from copy import deepcopy
from uuid import uuid1

import filetype
import pytest
from fastapi.testclient import TestClient

from reportbro_designer_api.backend import DBBackend
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


def backend_test():
    """Test reportbro DBBackend api function."""
    data_path = FPATH + "/data/default_template.json"
    with open(data_path, "r", encoding="utf8") as fss:
        data_json_a = json.loads(fss.read())

    data_json_b = deepcopy(data_json_a)
    data_json_b["bbbb"] = "bbbb"

    # check template empty
    response = client.get("/api/templates/list")
    assert response.status_code == 200
    assert response.json() == {"code": 200, "error": "ok", "data": []}

    # ----------------------------------------------
    #        check version_id change by same id
    # ----------------------------------------------

    # create templates
    tid = str(uuid1())
    response = client.put(
        "/api/templates",
        json=ss.RequestCreateTemplate(
            tid=tid, template_name="a", template_type="b"
        ).dict(),
    )
    assert response.status_code == 200
    rrr_a = ss.TemplateDataResponse(**response.json()).data

    response = client.post(
        f"/api/templates/{tid}",
        json=ss.RequestUploadTemplate(report=data_json_b).dict(),
    )
    assert response.status_code == 200
    rrr_b = ss.TemplateDataResponse(**response.json()).data

    # check version_id by same id
    assert rrr_a.tid == rrr_b.tid and rrr_a.version_id != rrr_b.version_id

    # ----------------------------------------------
    #        check tid has one
    # ----------------------------------------------

    # check tid has one
    response = client.get("/api/templates/list")
    assert response.status_code == 200
    rrr = ss.TemplateListResponse(**response.json()).data
    assert len(rrr) == 1
    assert rrr[0].tid == rrr_b.tid and rrr[0].version_id == rrr_b.version_id

    # check s3 list version has tow
    response = client.get(f"/api/templates/{tid}/versions")
    assert response.status_code == 200
    rrr = ss.TemplateListResponse(**response.json()).data
    assert (
        len(rrr) == 2
        and rrr[0].tid == rrr_a.tid
        and rrr[1].tid == rrr_b.tid
        and rrr[0].version_id != rrr[1].version_id
    )

    # check template body and matedate
    response = client.get(f"/api/templates/{tid}/desc")
    assert response.status_code == 200
    data_b = ss.TemplateDescResponse(**response.json()).data

    response = client.get(
        f"/api/templates/{tid}/desc",
        params={"versionId": rrr_a.version_id},
    )
    assert response.status_code == 200
    data_a = ss.TemplateDescResponse(**response.json()).data

    assert data_a and data_a.report == data_json_a
    assert (
        data_b
        and data_b.report == data_json_b
        and data_b.version_id == rrr_b.version_id
    )
    assert (
        data_b.template_name == data_a.template_name
        and data_b.template_type == data_a.template_type
    )

    # ----------------------------------------------
    #        check 404, file not found
    # ----------------------------------------------

    # check 404, file not found
    response = client.get("/api/templates/error-id/desc")
    assert response.status_code == 503 and "template not found" in response.text
    response = client.get(
        f"/api/templates/{tid}/desc",
        params={"versionId": "error vid"},
    )
    assert response.status_code == 503 and "template not found" in response.text

    # ----------------------------------------------
    #        create templates two
    # ----------------------------------------------

    # check tid 2
    tid2 = str(uuid1())
    response = client.put(
        "/api/templates",
        json=ss.RequestCreateTemplate(
            tid=tid2, template_name="a", template_type="b"
        ).dict(),
    )
    assert response.status_code == 200
    rrr_c = ss.TemplateDataResponse(**response.json()).data

    response = client.post(
        f"/api/templates/{tid2}",
        json=ss.RequestUploadTemplate(report=data_json_a).dict(),
    )
    assert response.status_code == 200
    rrr_d = ss.TemplateDataResponse(**response.json()).data

    # check tid2 has two version
    response = client.get(f"/api/templates/{tid2}/versions")
    assert response.status_code == 200
    rrr = ss.TemplateListResponse(**response.json()).data
    assert (
        len(rrr) == 2
        and rrr[0].tid == rrr_c.tid
        and rrr[1].tid == rrr_d.tid
        and rrr[0].version_id != rrr[1].version_id
    )

    # check tid has two
    response = client.get("/api/templates/list")
    assert response.status_code == 200
    rrr = ss.TemplateListResponse(**response.json()).data
    assert len(rrr) == 2
    tids = [i.tid for i in rrr]
    assert rrr_b.tid != rrr_c.tid and rrr_b.tid in tids and rrr_c.tid in tids

    # recheck tid1 delete before
    response = client.get("/api/templates/list")
    assert response.status_code == 200
    rrr = ss.TemplateListResponse(**response.json()).data
    assert len(rrr) == 2
    response = client.get(f"/api/templates/{tid}/versions")
    assert response.status_code == 200
    rrr = ss.TemplateListResponse(**response.json()).data
    assert (
        len(rrr) == 2
        and rrr[0].tid == rrr[1].tid == tid
        and rrr[0].version_id != rrr[1].version_id
    )

    # delete by version
    response = client.delete(
        f"/api/templates/{tid}",
        params={"versionId": rrr_b.version_id},
    )
    assert response.status_code == 200
    response = client.get(f"/api/templates/{tid}/versions")
    assert response.status_code == 200
    rrr = ss.TemplateListResponse(**response.json()).data
    assert len(rrr) == 1 and rrr[0].tid == rrr_a.tid
    response = client.get("/api/templates/list")
    assert response.status_code == 200
    rrr = ss.TemplateListResponse(**response.json()).data
    assert len(rrr) == 2
    response = client.get(f"/api/templates/{tid}/desc")
    assert response.status_code == 200
    rrr = ss.TemplateDescResponse(**response.json()).data
    assert rrr and rrr.version_id == rrr_a.version_id and rrr.report == data_a.report

    # delete all of tid2 key
    response = client.delete(f"/api/templates/{tid2}")
    assert response.status_code == 200
    response = client.get(f"/api/templates/{tid}/versions")
    assert response.status_code == 200
    rrr = ss.TemplateListResponse(**response.json()).data
    assert len(rrr) == 1 and rrr[0].tid == rrr_a.tid
    response = client.get(f"/api/templates/{tid2}/versions")
    assert response.status_code == 200
    rrr = ss.TemplateListResponse(**response.json()).data
    assert len(rrr) == 0
    response = client.get("/api/templates/list")
    assert response.status_code == 200
    rrr = ss.TemplateListResponse(**response.json()).data
    assert len(rrr) == 1
    response = client.get(f"/api/templates/{tid}/versions")
    assert response.status_code == 200
    rrr = ss.TemplateListResponse(**response.json()).data
    assert len(rrr) == 1 and rrr[0].tid == rrr_a.tid

    # ----------------------------------------------
    #        test clone template
    # ----------------------------------------------

    # get last tid version
    response = client.get(f"/api/templates/{tid}/desc")
    assert response.status_code == 200
    data_tid = ss.TemplateDescResponse(**response.json()).data

    # save data for cccccc key
    data_json_c = deepcopy(data_json_a)
    data_json_c["cccccc"] = "cccccc"
    response = client.post(
        f"/api/templates/{tid}",
        json=ss.RequestUploadTemplate(report=data_json_c).dict(),
    )
    assert response.status_code == 200

    # check cccc status
    response = client.get(f"/api/templates/{tid}/desc")
    assert response.status_code == 200
    rrr_ccc = ss.TemplateDescResponse(**response.json()).data
    assert rrr_ccc.report == data_json_c

    tid3 = str(uuid1())
    response = client.put(
        "/api/templates",
        json=ss.RequestCreateTemplate(
            tid=tid3, template_name="a", template_type="b"
        ).dict(),
    )
    assert response.status_code == 200
    rrr_clone_a = ss.TemplateDataResponse(**response.json()).data

    # clone templates with tid
    response = client.post(
        f"/api/templates/{tid3}/clone",
        json=ss.RequestCloneTemplate(
            from_tid=tid, from_version_id=data_tid.version_id
        ).dict(),
    )
    assert response.status_code == 200
    rrr_clone_b = ss.TemplateDataResponse(**response.json()).data
    assert (
        rrr_clone_a.tid == rrr_clone_b.tid
        and rrr_clone_a.version_id != rrr_clone_b.version_id
    )

    response = client.get(f"/api/templates/{rrr_clone_a.tid}/desc")
    assert response.status_code == 200
    data_clone_b = ss.TemplateDescResponse(**response.json()).data
    assert data_clone_b.report != data_json_c and data_clone_b.report == data_tid.report

    # clone templates with tid without version
    response = client.post(
        f"/api/templates/{tid3}/clone",
        json=ss.RequestCloneTemplate(from_tid=tid, from_version_id=None).dict(),
    )
    assert response.status_code == 200
    rrr_clone_b = ss.TemplateDataResponse(**response.json()).data
    assert (
        rrr_clone_a.tid == rrr_clone_b.tid
        and rrr_clone_a.version_id != rrr_clone_b.version_id
    )
    response = client.get(f"/api/templates/{rrr_clone_a.tid}/desc")
    assert response.status_code == 200
    data_clone_c = ss.TemplateDescResponse(**response.json()).data
    assert data_clone_c.report == data_json_c and data_clone_c.report != data_tid.report


def web_api_non_ascii():
    """Test web api."""
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


@pytest.mark.asyncio
async def test_s3_api(s3cli: S3Backend):
    """Test s3 reportbro api function."""
    assert s3cli
    backend_test()
    web_api_non_ascii()


@pytest.mark.asyncio
async def test_pgsql_api(pgsql_cli: DBBackend):
    """Test s3 reportbro api function."""
    assert pgsql_cli
    backend_test()
    web_api_non_ascii()


@pytest.mark.asyncio
async def test_mysql_api(mysql_cli: DBBackend):
    """Test s3 reportbro api function."""
    assert mysql_cli
    backend_test()
    web_api_non_ascii()


@pytest.mark.asyncio
async def test_sqlite_api(sqlite_cli: DBBackend):
    """Test s3 reportbro api function."""
    assert sqlite_cli
    backend_test()
    web_api_non_ascii()


@pytest.fixture(name="default_template")
def fixture_default_template():
    """default_template."""
    # check s3 empty
    response = client.get("/api/templates/list")
    assert response.status_code == 200
    assert response.json() == {"code": 200, "error": "ok", "data": []}

    # create templates
    response = client.put(
        "/api/templates",
        json=ss.RequestCreateTemplate(
            tid=None, template_name="test", template_type="test"
        ).dict(),
    )
    assert response.status_code == 200
    tid_ = ss.TemplateDataResponse(**response.json()).data
    tid = tid_.tid
    version_id = tid_.version_id
    assert tid and version_id and "/" not in tid
    assert tid_.template_name == tid_.template_type == "test"

    # get templates desc
    response = client.get(
        f"/api/templates/{tid}/desc",
        params={"versionId": version_id},
    )
    assert response.status_code == 200
    desc = ss.TemplateDescResponse(**response.json()).data
    assert "/" not in desc.tid and desc.report
    assert desc.template_name == desc.template_type == "test"
    return desc


def web_generate_pdf_review(default_template: ss.TemplateDescData):
    """Test web api generate pdf review."""
    report = default_template.report
    tid = default_template.tid
    # version_id = tempdata["versionId"]

    out_path = FPATH + "/../out"
    data_path = FPATH + "/data/default_template_data.json"
    with open(data_path, "r", encoding="utf8") as fss:
        data_json = json.loads(fss.read())

    response = client.put(
        "/api/templates/review",
        json=ss.RequestReviewTemplate(
            output_format="pdf",
            data=data_json,
            report=report,
            is_test_data=True,
        ).dict(),
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
        json=ss.RequestReviewTemplate(
            output_format="pdf",
            data=data_json,
            report=report,
            is_test_data=False,
        ).dict(),
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
        json=ss.RequestGenerateTemplate(
            output_format="pdf",
            data=data_json,
        ).dict(),
    )
    assert response.status_code == 200
    rrr = ss.TemplateDownLoadResponse(**response.json()).data
    assert rrr.download_key.startswith("key:") and rrr.download_url

    download_url = rrr.download_url
    filekey = rrr.download_key
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


async def web_generate_pdf_mutil(
    s3storage: S3Storage,
    default_template: ss.TemplateDescData,
):
    """Test web api generate pdf."""
    # report = default_template.report
    tid = default_template.tid
    version_id = default_template.version_id

    out_path = FPATH + "/../out"
    testfile_path = FPATH + "/data/testfile.pdf"
    data_path = FPATH + "/data/default_template_data.json"
    with open(data_path, "r", encoding="utf8") as fss:
        data_json = json.loads(fss.read())

    object_key = "testfile.pdf"
    with open(testfile_path, "rb") as ffs:
        await s3storage.put_file(f"s3:///{object_key}", ffs.read())
        testfile_url = await s3storage.generate_presigned_url(f"s3:///{object_key}")

    # test gen mutil
    response = client.put(
        "/api/templates/multi/generate",
        json=ss.RequestMultiGenerateTemplate(
            output_format="pdf",
            templates=[
                ss.RequestGenerateDataTemplate(
                    tid=tid, version_id=version_id, data=data_json
                ),
                ss.RequestGenerateDataTemplate(
                    tid=tid, version_id=version_id, data=data_json
                ),
            ],
        ).dict(),
    )
    assert response.status_code == 200
    rrr = ss.TemplateDownLoadResponse(**response.json()).data
    assert rrr.download_key.startswith("key:") and rrr.download_url

    download_url = rrr.download_url
    filekey = rrr.download_key
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
        json=ss.RequestMultiGenerateTemplate(
            output_format="pdf",
            templates=[
                ss.RequestGenerateDataTemplate(
                    tid=tid, version_id=version_id, data=data_json
                ),
                ss.RequestGenerateUrlTemplate(
                    pdf_url="file://" + multi_data_path,
                ),
                ss.RequestGenerateUrlTemplate(
                    pdf_url=testfile_url,
                ),
                ss.RequestGenerateDataTemplate(
                    tid=tid, version_id=version_id, data=data_json
                ),
            ],
        ).dict(),
    )
    assert response.status_code == 200
    rrr = ss.TemplateDownLoadResponse(**response.json()).data
    assert rrr.download_key.startswith("key:") and rrr.download_url

    download_url = rrr.download_url
    filekey = rrr.download_key
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
    with open(out_path + "/multi_download_data_url.pdf", "wb") as fss:
        fss.write(response.content)


@pytest.mark.asyncio
async def test_s3_pdf_generate(
    s3cli: S3Backend,
    s3storage: S3Storage,
    default_template: ss.TemplateDescData,
):
    """Test s3 reportbro api function."""
    assert s3cli
    web_generate_pdf_review(default_template)
    await web_generate_pdf_mutil(s3storage, default_template)


@pytest.mark.asyncio
async def test_pgsql_pdf_generate(
    pgsql_cli: DBBackend,
    s3storage: S3Storage,
    default_template: ss.TemplateDescData,
):
    """Test s3 reportbro api function."""
    assert pgsql_cli
    web_generate_pdf_review(default_template)
    await web_generate_pdf_mutil(s3storage, default_template)


@pytest.mark.asyncio
async def test_mysql_pdf_generate(
    mysql_cli: DBBackend,
    s3storage: S3Storage,
    default_template: ss.TemplateDescData,
):
    """Test s3 reportbro api function."""
    assert mysql_cli
    web_generate_pdf_review(default_template)
    await web_generate_pdf_mutil(s3storage, default_template)


@pytest.mark.asyncio
async def test_sqlite_pdf_generate(
    sqlite_cli: DBBackend,
    s3storage: S3Storage,
    default_template: ss.TemplateDescData,
):
    """Test s3 reportbro api function."""
    assert sqlite_cli
    web_generate_pdf_review(default_template)
    await web_generate_pdf_mutil(s3storage, default_template)
