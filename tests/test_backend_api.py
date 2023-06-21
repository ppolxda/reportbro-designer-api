# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 18:42:56.

@author: ppolxda

@desc: test s3 client api
"""
import pytest

from reportbro_designer_api.backend import BackendBase
from reportbro_designer_api.backend import DBBackend
from reportbro_designer_api.backend import S3Backend

# from reportbro_designer_api.backend.s3 import ClientError


async def backend_test(backendcli: BackendBase):
    """Test reportbro DBBackend api function."""
    body_a = {"aaa": ""}
    body_b = {"bbb": ""}

    _id = backendcli.gen_uuid()
    # check version_id by same id
    rrr_a = await backendcli.put_template("a", "b", body_a, tid=_id)
    rrr_b = await backendcli.put_template("a", "c", body_b, tid=_id)
    assert rrr_a.tid == rrr_b.tid and rrr_a.version_id != rrr_b.version_id

    # check tid has one
    rrr = await backendcli.get_templates_list()
    assert len(rrr) == 1
    assert rrr[0].tid == rrr_b.tid and rrr[0].version_id == rrr_b.version_id
    rrr = await backendcli.get_templates_version_list(_id)
    assert (
        len(rrr) == 2
        and rrr[0].tid == rrr_a.tid
        and rrr[1].tid == rrr_b.tid
        and rrr[0].version_id != rrr[1].version_id
    )

    # check template body and matedate
    data_b = await backendcli.get_template(rrr_b.tid)
    data_a = await backendcli.get_template(rrr_a.tid, rrr_a.version_id)
    assert data_a and data_a.report == body_a
    assert data_b and data_b.report == body_b and data_b.version_id == rrr_b.version_id
    assert (
        data_b.template_name == data_a.template_name
        and data_b.template_type != data_a.template_type
    )

    # check 404, file not found
    r = await backendcli.get_template("error id")
    assert r is None
    r = await backendcli.get_template(rrr_b.tid, "error vid")
    assert r is None

    # check tid 2
    _id2 = backendcli.gen_uuid()
    rrr_c = await backendcli.put_template("a", "b", body_a, tid=_id2)
    rrr_d = await backendcli.put_template("a", "d", body_b, tid=_id2)
    assert rrr_c
    rrr = await backendcli.get_templates_version_list(_id2)
    assert (
        len(rrr) == 2
        and rrr[0].tid == rrr_c.tid
        and rrr[1].tid == rrr_d.tid
        and rrr[0].version_id != rrr[1].version_id
    )

    # check tid has two
    rrr = await backendcli.get_templates_list()
    assert len(rrr) == 2
    tids = [i.tid for i in rrr]
    assert rrr_b.tid != rrr_c.tid and rrr_b.tid in tids and rrr_c.tid in tids

    # check delete
    rrr = await backendcli.get_templates_list()
    assert len(rrr) == 2
    rrr = await backendcli.get_templates_version_list(_id)
    assert (
        len(rrr) == 2
        and rrr[0].tid == rrr[1].tid == _id
        and rrr[0].version_id != rrr[1].version_id
    )

    # delete by version
    await backendcli.delete_template(_id, rrr_b.version_id)
    rrr = await backendcli.get_templates_version_list(_id)
    assert len(rrr) == 1 and rrr[0].tid == rrr_a.tid
    rrr = await backendcli.get_templates_list()
    assert len(rrr) == 2
    rrr = await backendcli.get_template(_id)
    assert rrr and rrr.version_id == rrr_a.version_id and rrr.report == data_a.report

    # delete all key
    await backendcli.delete_template(_id2)
    rrr = await backendcli.get_templates_version_list(_id)
    assert len(rrr) == 1 and rrr[0].tid == rrr_a.tid
    # with pytest.raises(ClientError):
    rrr = await backendcli.get_templates_version_list(_id2)
    assert len(rrr) == 0
    rrr = await backendcli.get_templates_list()
    assert len(rrr) == 1
    rrr = await backendcli.get_templates_version_list(_id)
    assert len(rrr) == 1 and rrr[0].tid == rrr_a.tid


@pytest.mark.asyncio
async def test_s3_api(s3cli: S3Backend):
    """Test s3 reportbro api function."""
    await backend_test(s3cli)


@pytest.mark.asyncio
async def test_pgsql_api(pgsql_cli: DBBackend):
    """Test s3 reportbro api function."""
    await backend_test(pgsql_cli)


@pytest.mark.asyncio
async def test_mysql_api(mysql_cli: DBBackend):
    """Test s3 reportbro api function."""
    await backend_test(mysql_cli)


@pytest.mark.asyncio
async def test_sqlite_api(sqlite_cli: DBBackend):
    """Test s3 reportbro api function."""
    await backend_test(sqlite_cli)
