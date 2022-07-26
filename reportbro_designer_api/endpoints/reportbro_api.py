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

from ..settings import FONTS_LOADER
from ..settings import ReportbroS3Client
from ..settings import get_s3_client
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
    s3cli: ReportbroS3Client = Depends(get_s3_client),
):
    """Get templates List."""
    list_: List[dict] = s3cli.get_templates_list()
    return TemplateListResponse(
        code=HTTP_200_OK,
        error="ok",
        data=[
            TemplateListData(
                **{
                    **i,
                    "template_designer_page": request.url_for(
                        "Templates Designer page", tid=i["tid"]
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
    s3cli: ReportbroS3Client = Depends(get_s3_client),
):
    """Get templates List."""
    list_ = s3cli.get_templates_version_list(tid)
    return TemplateListResponse(
        code=HTTP_200_OK,
        error="ok",
        data=[
            TemplateListData(
                **{
                    **i,
                    "template_designer_page": request.url_for(
                        "Templates Designer page", tid=i["tid"]
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
    s3cli: ReportbroS3Client = Depends(get_s3_client),
):
    """Get templates List."""
    list_ = s3cli.get_templates(tid, version_id)
    return TemplateDescResponse(
        code=HTTP_200_OK,
        error="ok",
        data=TemplateDescData(
            **{
                **list_,
                "report": list_["template_body"],
                "template_designer_page": request.url_for(
                    "Templates Designer page", tid=list_["tid"]
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
    s3cli: ReportbroS3Client = Depends(get_s3_client),
):
    """Templates Manage page."""
    key = s3cli.gen_uuid_object_key()
    rrr = s3cli.put_templates(key, req.template_name, req.template_type, {})
    return TemplateDataResponse(
        code=HTTP_200_OK,
        error="ok",
        data=TemplateListData(
            template_name=req.template_name,
            template_type=req.template_type,
            tid=rrr["tid"],
            version_id=rrr["version_id"],
            template_designer_page=request.url_for(
                "Templates Designer page", tid=rrr["tid"]
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
    s3cli: ReportbroS3Client = Depends(get_s3_client),
):
    """Save Templates."""
    if not req.report:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="report is empty",
        )

    obj = s3cli.get_templates_object(tid)
    rrr = s3cli.put_templates(
        tid,
        obj.metadata["template_name"],
        obj.metadata["template_type"],
        req.report,
    )
    return TemplateDataResponse(
        code=HTTP_200_OK,
        error="ok",
        data=TemplateListData(
            template_name=obj.metadata["template_name"],
            template_type=obj.metadata["template_type"],
            tid=tid,
            version_id=rrr["version_id"],
            template_designer_page=request.url_for(
                "Templates Designer page", tid=rrr["tid"]
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
    s3cli: ReportbroS3Client = Depends(get_s3_client),
):
    """Clone Templates."""
    obj = s3cli.get_templates(req.from_tid, req.from_version_id)

    if not req.from_version_id:
        req.from_version_id = obj["version_id"]

    if tid == req.from_tid and obj["version_id"] == req.from_version_id:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="tid, from_tid must not same",
        )

    obj_src = s3cli.get_templates(tid)
    rrr = s3cli.put_templates(
        tid,
        obj_src["template_name"],
        obj_src["template_type"],
        obj["template_body"],
    )
    return TemplateDataResponse(
        code=HTTP_200_OK,
        error="ok",
        data=TemplateListData(
            template_name=obj_src["template_name"],
            template_type=obj_src["template_type"],
            tid=tid,
            version_id=rrr["version_id"],
            template_designer_page=request.url_for(
                "Templates Designer page", tid=rrr["tid"]
            ),
        ),
    )


@router.delete(
    "/templates/{tid}/delete",
    tags=TAGS,
    name="Delete Templates",
    response_model=ErrorResponse,
)
async def delete_templates(
    tid: str = Path(title="Template id"),
    version_id: Optional[str] = Query(
        None, title="Template version id", alias="versionId"
    ),
    s3cli: ReportbroS3Client = Depends(get_s3_client),
):
    """Delete Templates."""
    s3cli.delete_templates_version(tid, version_id)
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
    now = datetime.now()
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
        # in case an error occurs during report report generation
        # a ReportBroError exception is thrown
        # to stop processing. We return this error within a list so the error can be
        # processed by ReportBro Designer.
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"failed to generation report[{ex}]",
        ) from ex
    finally:
        end = timer()
        LOGGER.info("pdf generated in %.3f seconds", (end - start))


def read_file_in_s3(output_format, key, s3cli):
    """Read file in s3."""
    if output_format not in ("pdf", "xlsx"):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="outputFormat parameter missing or invalid",
        )

    if key.startswith("key:"):
        key = key[4:]

    pdfdata = s3cli.get_review(output_format, key)
    filename = pdfdata["filename"]
    report_file = pdfdata["data"]

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
    "/templates/review",
    tags=GEN_TAGS,
    name="Generate preview file from template",
)
async def review_templates_gen(
    req: RequestReviewTemplate,
    disabled_fill: bool = Query(
        default=False, title="Disable fill empty fields for input data"
    ),
    s3cli: ReportbroS3Client = Depends(get_s3_client),
):
    """Review Templates Generate."""
    filename, report_file = gen_file_from_report(
        req.output_format, req.report, req.data, req.is_test_data, disabled_fill
    )
    assert report_file
    s3file = s3cli.put_review(req.output_format, report_file, filename)
    key = "key:" + str(s3file["version_id"])
    return PlainTextResponse(key)


@router.get(
    "/templates/review",
    tags=GEN_TAGS,
    name="Get generate preview file",
)
async def review_templates(
    output_format: str = Query(
        "pdf", title="Output Format(pdf|xlsx)", regex=r"^(pdf|xlsx)$"
    ),
    key: str = Query(title="File Key", min_length=16),
    s3cli: ReportbroS3Client = Depends(get_s3_client),
):
    """Review Templates."""
    return read_file_in_s3(output_format, key, s3cli)


# ----------------------------------------------
#        PDF REPORT Multiple Generate
# ----------------------------------------------


@router.put(
    "/templates/multi/generate",
    tags=GEN_TAGS,
    name="Generate file from multiple template(PDF Only)",
    response_model=TemplateDownLoadResponse,
)
async def generation_templates_multi_gen(
    request: Request,
    req: RequestMultiGenerateTemplate,
    disabled_fill: bool = Query(
        default=False, title="Disable fill empty fields for input data"
    ),
    s3cli: ReportbroS3Client = Depends(get_s3_client),
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
            obj = s3cli.get_templates(i.tid, i.version_id)
            filename, report_file = gen_file_from_report(
                req.output_format,
                obj["template_body"],
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
    s3file = s3cli.put_review(req.output_format, rrr.read(), filename)
    key = "key:" + str(s3file["version_id"])
    return TemplateDownLoadResponse(
        code=HTTP_200_OK,
        error="ok",
        data=TemplateDownLoadData(
            download_key=key,
            download_url=request.url_for("Get generate file from multiple template")
            + "?"
            + urlencode(
                {
                    "key": key,
                }
            ),
        ),
    )


@router.get(
    "/templates/multi/generate",
    tags=GEN_TAGS,
    name="Get generate file from multiple template",
)
async def generation_templates_multi(
    key: str = Query(title="File Key", min_length=16),
    s3cli: ReportbroS3Client = Depends(get_s3_client),
):
    """Review Templates."""
    return read_file_in_s3("pdf", key, s3cli)


# ----------------------------------------------
#        PDF REPORT Generate
# ----------------------------------------------


@router.put(
    "/templates/{tid}/generate",
    tags=GEN_TAGS,
    name="Generate file from template",
    response_model=TemplateDownLoadResponse,
)
async def generation_templates_gen(
    request: Request,
    req: RequestGenerateTemplate,
    tid: str = Path(title="Template id"),
    version_id: Optional[str] = Query(
        None, title="Template version id", alias="versionId"
    ),
    disabled_fill: bool = Query(
        default=False, title="Disable fill empty fields for input data"
    ),
    s3cli: ReportbroS3Client = Depends(get_s3_client),
):
    """Review Templates Generate."""
    obj = s3cli.get_templates(tid, version_id)
    filename, report_file = gen_file_from_report(
        req.output_format, obj["template_body"], req.data, False, disabled_fill
    )
    assert report_file
    s3file = s3cli.put_review(req.output_format, report_file, filename)
    key = "key:" + str(s3file["version_id"])
    return TemplateDownLoadResponse(
        code=HTTP_200_OK,
        error="ok",
        data=TemplateDownLoadData(
            download_key=key,
            download_url=request.url_for("Get generate file", tid=tid)
            + "?"
            + urlencode(
                {
                    "key": key,
                }
            ),
        ),
    )


@router.get(
    "/templates/{tid}/generate",
    tags=GEN_TAGS,
    name="Get generate file",
)
async def generation_templates(
    output_format: str = Query(
        "pdf", title="Output Format(pdf|xlsx)", regex=r"^(pdf|xlsx)$"
    ),
    key: str = Query(title="File Key", min_length=16),
    s3cli: ReportbroS3Client = Depends(get_s3_client),
):
    """Review Templates."""
    return read_file_in_s3(output_format, key, s3cli)
