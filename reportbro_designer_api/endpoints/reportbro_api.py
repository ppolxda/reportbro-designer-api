# -*- coding: utf-8 -*-
"""
@create: 2022-07-25 10:39:19.

@author: ppolxda

@desc: ReportBro Api
"""
import traceback
from datetime import datetime
from enum import Enum
from io import BytesIO
from timeit import default_timer as timer
from typing import List
from typing import Optional
from typing import Union

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
from .reportbro_schema import RequestCloneTemplate
from .reportbro_schema import RequestCreateTemplate
from .reportbro_schema import RequestGenerateTemplate
from .reportbro_schema import RequestReviewTemplate
from .reportbro_schema import RequestUploadTemplate
from .reportbro_schema import TemplateDataResponse
from .reportbro_schema import TemplateDescData
from .reportbro_schema import TemplateDescResponse
from .reportbro_schema import TemplateListData
from .reportbro_schema import TemplateListResponse

router = APIRouter()
TAGS: List[Union[str, Enum]] = ["ReportBro Api"]
# templates = Jinja2Templates(directory=settings.TEMPLATES_PATH)


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
    response_model=ErrorResponse,
)
async def save_templates(
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
    s3cli.put_templates(
        tid,
        obj.metadata["template_name"],
        obj.metadata["template_type"],
        req.report,
    )
    return ErrorResponse(code=HTTP_200_OK, error="ok")


@router.post(
    "/templates/{tid}/clone",
    tags=TAGS,
    name="Clone Templates",
    response_model=ErrorResponse,
)
async def clone_templates(
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

    s3cli.put_templates(
        tid,
        obj["template_name"],
        obj["template_type"],
        obj["report"],
    )
    return ErrorResponse(code=HTTP_200_OK, error="ok")


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
#        代码段描述
# ----------------------------------------------


def gen_file_from_report(output_format, report_definition, data, is_test_data):
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
        report = ReportPdf(report_definition, data, FONTS_LOADER, is_test_data)
    except ReportBroError as ex:
        LOGGER.warning(
            "failed to initialize report: %s %s", str(ex), traceback.format_exc()
        )
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="failed to initialize report[{}]".format(ex),
        ) from ex

    if report.report.errors:
        # return list of errors in case report contains errors, e.g. duplicate parameters.
        # with this information ReportBro Designer can select object containing errors,
        # highlight erroneous fields and display error messages
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="\n".join(report.report.errors),
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
        # in case an error occurs during report report generation a ReportBroError exception is thrown
        # to stop processing. We return this error within a list so the error can be
        # processed by ReportBro Designer.
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="failed to generation report[{}]".format(ex),
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
    tags=TAGS,
    name="Generate preview file from template",
)
async def review_templates_gen(
    req: RequestReviewTemplate,
    s3cli: ReportbroS3Client = Depends(get_s3_client),
):
    """Review Templates Generate."""
    filename, report_file = gen_file_from_report(
        req.output_format, req.report, req.data, req.is_test_data
    )
    s3file = s3cli.put_review(req.output_format, report_file, filename)
    key = "key:" + str(s3file["version_id"])
    return PlainTextResponse(key)


@router.get(
    "/templates/review",
    tags=TAGS,
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
#        代码段描述
# ----------------------------------------------


@router.put(
    "/templates/{tid}/generate",
    tags=TAGS,
    name="Generate file from template",
)
async def generation_templates_gen(
    req: RequestGenerateTemplate,
    tid: str = Path(title="Template id"),
    version_id: Optional[str] = Query(
        None, title="Template version id", alias="versionId"
    ),
    s3cli: ReportbroS3Client = Depends(get_s3_client),
):
    """Review Templates Generate."""
    obj = s3cli.get_templates(tid, version_id)
    filename, report_file = gen_file_from_report(
        req.output_format,
        obj["template_body"],
        req.data,
        False,
    )
    s3file = s3cli.put_review(req.output_format, report_file, filename)
    key = "key:" + str(s3file["version_id"])
    return PlainTextResponse(key)


@router.get(
    "/templates/{tid}/generate",
    tags=TAGS,
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
