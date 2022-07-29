# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 18:42:56.

@author: ppolxda

@desc: test s3 client api
"""
import pytest

from reportbro_designer_api.utils.s3 import ClientError
from reportbro_designer_api.utils.s3 import ReportbroS3Client


@pytest.mark.usefixtures()
def test_s3_api(s3cli: ReportbroS3Client):
    """Test s3 reportbro api function."""
    body = {"aaa": ""}

    _id = s3cli.gen_uuid_object_key()
    rrr_a = s3cli.put_templates(_id, "a", "b", body)
    rrr_b = s3cli.put_templates(_id, "a", "c", body)
    assert rrr_a["tid"] == rrr_b["tid"] and rrr_a["version_id"] != rrr_b["version_id"]
    rrr = s3cli.get_templates_list()
    assert len(rrr) == 1
    assert rrr[0]["tid"] == rrr_b["tid"] and rrr[0]["version_id"] == rrr_b["version_id"]
    data_a = s3cli.get_templates(rrr_b["tid"])
    assert data_a["template_body"] == body
    data_b = s3cli.get_templates(rrr_b["tid"], rrr_a["version_id"])
    assert (
        data_b["template_body"] == body and data_b["version_id"] == rrr_a["version_id"]
    )
    assert (
        data_b["template_name"] == data_a["template_name"]
        and data_b["template_type"] != data_a["template_type"]
    )
    with pytest.raises(ClientError):
        s3cli.get_templates("error id")

    with pytest.raises(ClientError):
        s3cli.get_templates(rrr_b["tid"], "error vid")

    _id2 = s3cli.gen_uuid_object_key()
    rrr_c = s3cli.put_templates(_id2, "a", "b", body)
    rrr_d = s3cli.put_templates(_id2, "a", "d", body)
    assert rrr_c
    rrr = s3cli.get_templates_version_list(_id2)
    assert (
        len(rrr) == 2
        and rrr[0]["tid"] == rrr_c["tid"]
        and rrr[1]["tid"] == rrr_d["tid"]
        and rrr[0]["version_id"] != rrr[1]["version_id"]
    )

    # check delete
    rrr = s3cli.get_templates_list()
    assert len(rrr) == 2
    rrr = s3cli.get_templates_version_list(_id)
    assert (
        len(rrr) == 2
        and rrr[0]["tid"] == rrr_b["tid"]
        and rrr[1]["tid"] == rrr_b["tid"]
    )
    # delete by version
    s3cli.delete_templates_version(_id, rrr_b["version_id"])
    rrr = s3cli.get_templates_version_list(_id)
    assert len(rrr) == 1 and rrr[0]["tid"] == rrr_a["tid"]
    rrr = s3cli.get_templates_list()
    assert len(rrr) == 2

    # delete all key
    s3cli.delete_templates_version(_id2)
    rrr = s3cli.get_templates_version_list(_id)
    assert len(rrr) == 1 and rrr[0]["tid"] == rrr_a["tid"]
    # with pytest.raises(ClientError):
    rrr = s3cli.get_templates_version_list(_id2)
    assert len(rrr) == 0
    rrr = s3cli.get_templates_list()
    assert len(rrr) == 1
    rrr = s3cli.get_templates_version_list(_id)
    assert len(rrr) == 1 and rrr[0]["tid"] == rrr_a["tid"]
