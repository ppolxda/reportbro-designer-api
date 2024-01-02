# -*- coding: utf-8 -*-
"""
@create: 2022-07-25 10:39:19.

@author: ppolxda

@desc: ReportBro Api
"""
import json
import os
import traceback
from datetime import datetime
from enum import Enum
from io import BytesIO
from timeit import default_timer as timer
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import urlencode

import filetype
import PyPDF2
import requests
from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Path
from fastapi import Query
from fastapi import Request
from fastapi.responses import PlainTextResponse
from fastapi.responses import StreamingResponse
from reportbro import ReportBroError
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_400_BAD_REQUEST

from ..backend.backends.base import BackendBase
from ..clients import FONTS_LOADER
from ..clients import StorageMange
from ..clients import get_meth_cli
from ..clients import get_storage_mange
from ..errors import TemplageNotFoundError
from ..settings import settings
from ..utils.logger import LOGGER
from ..utils.model import ErrorResponse
from ..utils.report import ReportPdf
from ..utils.report import fill_default
from .reportbro_schema import RequestCloneTemplate
from .reportbro_schema import RequestCreateTemplate
from .reportbro_schema import RequestGenerateDataTemplate
from .reportbro_schema import RequestGenerateTemplate
from .reportbro_schema import RequestGenerateUrlTemplate
from .reportbro_schema import RequestMultiGenerateTemplate
from .reportbro_schema import RequestReviewTemplate
from .reportbro_schema import RequestUploadTemplate
from .reportbro_schema import TemplateDataResponse
from .reportbro_schema import TemplateDescData
from .reportbro_schema import TemplateDescResponse
from .reportbro_schema import TemplateDownLoadData
from .reportbro_schema import TemplateDownLoadResponse
from .reportbro_schema import TemplateListData
from .reportbro_schema import TemplateListResponse

router = APIRouter()
TAGS: List[Union[str, Enum]] = ["ReportBro Api"]
GEN_TAGS: List[Union[str, Enum]] = ["ReportBro Generate Api"]
# templates = Jinja2Templates(directory=settings.TEMPLATES_PATH)


def is_pdf(data: bytes):
    """is_pdf."""
    rtype = filetype.guess(data)
    return rtype and rtype.extension == "pdf"


@router.get(
    "/templates/list",
    tags=TAGS,
    name="Get templates List",
    response_model=TemplateListResponse,
)
async def main_index_page(
    request: Request,
    client: BackendBase = Depends(get_meth_cli),
):
    """Get templates List."""
    list_ = await client.get_templates_list(limit=settings.PAGE_LIMIT)
    return TemplateListResponse(
        code=HTTP_200_OK,
        error="ok",
        data=[
            TemplateListData(
                **{
                    **i.__dict__,
                    "template_designer_page": str(
                        request.url_for("Templates Designer page", tid=i.tid)
                    ),
                }
            )
            for i in list_
        ],
    )


@router.get(
    "/templates/{tid}/versions",
    tags=TAGS,
    name="Get templates Versions",
    response_model=TemplateListResponse,
)
async def get_versions(
    request: Request,
    tid: str = Path(title="Template id"),
    client: BackendBase = Depends(get_meth_cli),
):
    """Get templates List."""
    list_ = await client.get_templates_version_list(tid)
    return TemplateListResponse(
        code=HTTP_200_OK,
        error="ok",
        data=[
            TemplateListData(
                **{
                    **i.__dict__,
                    "template_designer_page": str(
                        request.url_for("Templates Designer page", tid=i.tid)
                    ),
                }
            )
            for i in list_
        ],
    )


@router.get(
    "/templates/{tid}/desc",
    tags=TAGS,
    name="Get templates Data",
    response_model=TemplateDescResponse,
)
async def get_templates_data(
    request: Request,
    tid: str = Path(title="Template id"),
    version_id: Optional[str] = Query(
        None, title="Template version id", alias="versionId"
    ),
    client: BackendBase = Depends(get_meth_cli),
):
    """Get templates List."""
    template = await client.get_template(tid, version_id)
    if not template:
        raise TemplageNotFoundError("template not found")

    return TemplateDescResponse(
        code=HTTP_200_OK,
        error="ok",
        data=TemplateDescData(
            **{
                **template.dict(),
                "report": template.report,
                "template_designer_page": str(
                    request.url_for("Templates Designer page", tid=template.tid)
                ),
            }
        ),
    )


@router.put(
    "/templates",
    tags=TAGS,
    name="Create Templates",
    response_model=TemplateDataResponse,
)
async def create_templates(
    request: Request,
    req: RequestCreateTemplate,
    client: BackendBase = Depends(get_meth_cli),
):
    """Templates Manage page."""
    rrr = await client.put_template(req.template_name, req.template_type, {})
    return TemplateDataResponse(
        code=HTTP_200_OK,
        error="ok",
        data=TemplateListData(
            updated_at=datetime.now(),
            template_name=req.template_name,
            template_type=req.template_type,
            tid=rrr.tid,
            version_id=rrr.version_id,
            template_designer_page=str(
                request.url_for("Templates Designer page", tid=rrr.tid)
            ),
        ),
    )


@router.put(
    "/templates/{tid}",
    tags=TAGS,
    name="Create Templates, use own tid",
    response_model=TemplateDataResponse,
)
async def create_templates_tid(
    request: Request,
    req: RequestCreateTemplate,
    tid: str = Path(title="Template id"),
    client: BackendBase = Depends(get_meth_cli),
):
    """Templates Manage page."""
    rrr = await client.put_template(req.template_name, req.template_type, {}, tid=tid)
    return TemplateDataResponse(
        code=HTTP_200_OK,
        error="ok",
        data=TemplateListData(
            updated_at=datetime.now(),
            template_name=req.template_name,
            template_type=req.template_type,
            tid=rrr.tid,
            version_id=rrr.version_id,
            template_designer_page=str(
                request.url_for("Templates Designer page", tid=rrr.tid)
            ),
        ),
    )


@router.post(
    "/templates/{tid}",
    tags=TAGS,
    name="Save Templates",
    response_model=TemplateDataResponse,
)
async def save_templates(
    request: Request,
    req: RequestUploadTemplate,
    tid: str = Path(title="Template id"),
    client: BackendBase = Depends(get_meth_cli),
):
    """Save Templates."""
    if not req.report:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="report is empty",
        )

    obj = await client.get_template(tid)
    if not obj:
        raise TemplageNotFoundError("template not found")

    rrr = await client.put_template(
        tid=tid,
        template_name=obj.template_name,
        template_type=obj.template_type,
        report=req.report,
    )
    return TemplateDataResponse(
        code=HTTP_200_OK,
        error="ok",
        data=TemplateListData(
            updated_at=datetime.now(),
            template_name=obj.template_name,
            template_type=obj.template_type,
            tid=tid,
            version_id=rrr.version_id,
            template_designer_page=str(
                request.url_for("Templates Designer page", tid=rrr.tid)
            ),
        ),
    )


@router.post(
    "/templates/{tid}/clone",
    tags=TAGS,
    name="Clone Templates",
    response_model=TemplateDataResponse,
)
async def clone_templates(
    request: Request,
    req: RequestCloneTemplate,
    tid: str = Path(title="Template id"),
    client: BackendBase = Depends(get_meth_cli),
):
    """Clone Templates."""
    obj = await client.get_template(req.from_tid, req.from_version_id)
    if not obj:
        raise TemplageNotFoundError("template not found")

    if not req.from_version_id:
        req.from_version_id = obj.version_id

    if tid == req.from_tid and obj.version_id == req.from_version_id:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="tid, from_tid must not same",
        )

    obj_src = await client.get_template(tid)
    if not obj_src:
        raise TemplageNotFoundError("template not found")

    rrr = await client.put_template(
        tid=tid,
        template_name=obj_src.template_name,
        template_type=obj_src.template_type,
        report=obj.report,
    )
    return TemplateDataResponse(
        code=HTTP_200_OK,
        error="ok",
        data=TemplateListData(
            updated_at=datetime.now(),
            template_name=obj_src.template_name,
            template_type=obj_src.template_type,
            tid=tid,
            version_id=rrr.version_id,
            template_designer_page=str(
                request.url_for("Templates Designer page", tid=rrr.tid)
            ),
        ),
    )


@router.delete(
    "/templates/{tid}",
    tags=TAGS,
    name="Delete Templates",
    response_model=ErrorResponse,
)
async def delete_templates(
    tid: str = Path(title="Template id"),
    version_id: Optional[str] = Query(
        None, title="Template version id", alias="versionId"
    ),
    client: BackendBase = Depends(get_meth_cli),
):
    """Delete Templates."""
    await client.delete_template(tid, version_id)
    return ErrorResponse(code=HTTP_200_OK, error="ok")


# ----------------------------------------------
#        PDF REPORT Generate
# ----------------------------------------------


def gen_file_from_report(
    output_format, report_definition, data, is_test_data, disabled_fill
):
    """Review Templates Generate."""
    # all data needed for report preview is sent in the initial PUT request, it contains
    # the format (pdf or xlsx), the report itself (report_definition), the data (test data
    # defined within parameters in the Designer) and is_test_data flag (always True
    # when request is sent from Designer)
    if output_format not in ("pdf", "xlsx"):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="outputFormat parameter missing or invalid",
        )

    try:
        if not disabled_fill:
            fill_default(report_definition, data)

        report = ReportPdf(report_definition, data, FONTS_LOADER, is_test_data)
    except ReportBroError as ex:
        LOGGER.warning(
            "failed to initialize report: %s %s", str(ex), traceback.format_exc()
        )
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"failed to initialize report[{ex}]",
        ) from ex

    if report.report.errors:
        # return list of errors in case report contains errors, e.g. duplicate parameters.
        # with this information ReportBro Designer can select object containing errors,
        # highlight erroneous fields and display error messages
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=json.dumps(report.report.errors),
        )

    start = timer()
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    try:
        if output_format == "pdf":
            report_file = report.generate_pdf(title=settings.PDF_TITLE)
            filename = "report-" + str(now) + ".pdf"
            return filename, report_file
        else:
            report_file = report.generate_xlsx()
            filename = "report-" + str(now) + ".xlsx"
            return filename, report_file
    except ReportBroError as ex:
        # in case an error occurs during report report generate
        # a ReportBroError exception is thrown
        # to stop processing. We return this error within a list so the error can be
        # processed by ReportBro Designer.
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"failed to generate report[{ex}]",
        ) from ex
    finally:
        end = timer()
        LOGGER.info("pdf generated in %.3f seconds", (end - start))


async def read_file_in_s3(output_format, key, client: StorageMange):
    """Read file in s3."""
    if output_format not in ("pdf", "xlsx"):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="outputFormat parameter missing or invalid",
        )

    filename, report_file = await client.get_file(key)

    if output_format == "pdf":
        response = StreamingResponse(
            BytesIO(report_file),
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="{filename}"'},
        )
    else:
        response = StreamingResponse(
            BytesIO(report_file),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'inline; filename="{filename}"'},
        )

    return response


@router.put(
    "/templates/review/generate",
    tags=GEN_TAGS,
    name="Generate preview file from template",
)
async def review_templates_gen(
    req: RequestReviewTemplate,
    background_tasks: BackgroundTasks,
    disabled_fill: bool = Query(
        default=False, title="Disable fill empty fields for input data"
    ),
    storage: StorageMange = Depends(get_storage_mange),
):
    """Review Templates Generate."""
    filename, report_file = gen_file_from_report(
        req.output_format, req.report, req.data, req.is_test_data, disabled_fill
    )
    assert report_file
    key = await storage.put_file(filename, report_file, background_tasks)
    return PlainTextResponse(key)


@router.get(
    "/templates/review/generate",
    tags=GEN_TAGS,
    name="Get generate preview file",
)
async def review_templates(
    output_format: str = Query(
        "pdf", title="Output Format(pdf|xlsx)", regex=r"^(pdf|xlsx)$"
    ),
    key: str = Query(title="File Key", min_length=16),
    storage: StorageMange = Depends(get_storage_mange),
):
    """Review Templates."""
    r = await read_file_in_s3(output_format, key, storage)
    return r


# ----------------------------------------------
#        PDF REPORT Multiple Generate
# ----------------------------------------------


@router.put(
    "/templates/multi/generate",
    tags=GEN_TAGS,
    name="Generate file from multiple template(PDF Only)",
    response_model=TemplateDownLoadResponse,
)
async def generate_templates_multi_gen(
    request: Request,
    req: RequestMultiGenerateTemplate,
    background_tasks: BackgroundTasks,
    disabled_fill: bool = Query(
        default=False, title="Disable fill empty fields for input data"
    ),
    client: BackendBase = Depends(get_meth_cli),
    storage: StorageMange = Depends(get_storage_mange),
):
    """Review Templates Generate."""
    if not req.templates:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="templates is empty",
        )

    filename = ""
    merge_file = PyPDF2.PdfFileMerger()
    for i in req.templates:
        if isinstance(i, RequestGenerateUrlTemplate):
            if i.pdf_url.startswith("file://"):
                with open(i.pdf_url[7:], "rb") as fss:
                    data = fss.read()
                filename, report_file = os.path.basename(i.pdf_url), data
            else:
                data = requests.get(i.pdf_url, timeout=settings.DOWNLOAD_TIMEOUT)
                filename, report_file = os.path.basename(i.pdf_url), data.content

            if not is_pdf(report_file):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="pdf_url is not pdf file",
                )
        elif isinstance(i, RequestGenerateDataTemplate):
            templage = await client.get_template(i.tid, i.version_id)
            if not templage:
                raise TemplageNotFoundError("template not found")

            filename, report_file = gen_file_from_report(
                req.output_format,
                templage.report,
                i.data,
                False,
                disabled_fill,
            )
        else:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="templates is invaild",
            )

        assert report_file
        merge_file.append(
            PyPDF2.PdfFileReader(stream=BytesIO(initial_bytes=report_file))
        )

    rrr = BytesIO()
    merge_file.write(rrr)
    rrr.seek(0)

    assert filename
    download_key = await storage.put_file(filename, rrr.read(), background_tasks)
    return TemplateDownLoadResponse(
        code=HTTP_200_OK,
        error="ok",
        data=TemplateDownLoadData(
            download_key=download_key,
            download_url=str(
                request.url_for("Get generate file from multiple template")
            )
            + "?"
            + urlencode(
                {
                    "key": download_key,
                }
            ),
        ),
    )


@router.get(
    "/templates/multi/generate",
    tags=GEN_TAGS,
    name="Get generate file from multiple template",
)
async def generate_templates_multi(
    key: str = Query(title="File Key", min_length=16),
    storage: StorageMange = Depends(get_storage_mange),
):
    """Review Templates."""
    r = await read_file_in_s3("pdf", key, storage)
    return r


# ----------------------------------------------
#        PDF REPORT Generate
# ----------------------------------------------


@router.put(
    "/templates/{tid}/generate",
    tags=GEN_TAGS,
    name="Generate file from template",
    response_model=TemplateDownLoadResponse,
)
async def generate_templates_gen(
    request: Request,
    req: RequestGenerateTemplate,
    background_tasks: BackgroundTasks,
    tid: str = Path(title="Template id"),
    version_id: Optional[str] = Query(
        None, title="Template version id", alias="versionId"
    ),
    disabled_fill: bool = Query(
        default=False, title="Disable fill empty fields for input data"
    ),
    client: BackendBase = Depends(get_meth_cli),
    storage: StorageMange = Depends(get_storage_mange),
):
    """Review Templates Generate."""
    templage = await client.get_template(tid, version_id)
    if not templage:
        raise TemplageNotFoundError("template not found")

    filename, report_file = gen_file_from_report(
        req.output_format, templage.report, req.data, False, disabled_fill
    )
    assert report_file
    download_key = await storage.put_file(filename, report_file, background_tasks)
    return TemplateDownLoadResponse(
        code=HTTP_200_OK,
        error="ok",
        data=TemplateDownLoadData(
            download_key=download_key,
            download_url=str(request.url_for("Get generate file", tid=tid))
            + "?"
            + urlencode(
                {
                    "key": download_key,
                }
            ),
        ),
    )


@router.get(
    "/templates/{tid}/generate",
    tags=GEN_TAGS,
    name="Get generate file",
)
async def generate_templates(
    output_format: str = Query(
        "pdf", title="Output Format(pdf|xlsx)", regex=r"^(pdf|xlsx)$"
    ),
    key: str = Query(title="File Key", min_length=16),
    storage: StorageMange = Depends(get_storage_mange),
):
    """Review Templates."""
    r = await read_file_in_s3(output_format, key, storage)
    return r
