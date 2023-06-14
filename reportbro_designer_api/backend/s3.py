# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 17:54:46.

@author: ppolxda

@desc: S3 Api
"""

import base64
import json
from contextlib import asynccontextmanager
from io import BytesIO
from typing import AsyncGenerator
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import aioboto3
from aiobotocore.config import AioConfig
from botocore.client import ClientError
from types_aiobotocore_s3.client import S3Client
from types_aiobotocore_s3.type_defs import HeadObjectOutputTypeDef
from types_aiobotocore_s3.type_defs import ObjectTypeDef
from types_aiobotocore_s3.type_defs import ObjectVersionTypeDef

from reportbro_designer_api.errors import S3ClientError

from . import schemas as sa
from .base import BackendBase


def hook_create_bucket_when_not_exist():
    """Create bucket when not exist."""

    def wrapper(func):
        async def wrapper_call(self, *args, **kwargs):
            await self.create_bucket_when_not_exist()
            return await func(self, *args, **kwargs)

        return wrapper_call

    return wrapper


def hook_object_not_exist():
    """Create bucket when not exist."""

    def wrapper(func):
        async def wrapper_call(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except ClientError as ex:
                if ex.response.get("Error", {}).get("Code", "") in ["404", "NoSuchKey"]:
                    return None

        return wrapper_call

    return wrapper


class S3BackendClient(object):
    """S3Backend."""

    TEMPLATES_PREFIX = "templates"
    REVIEW_PREFIX = "review"

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        endpoint_url: Optional[str] = None,
        region_name: str = "us-east-1",
        bucket: str = "reportbro",
        project: str = "default",
        default_template: Optional[dict] = None,
        query_max_limit: int = 1000,
    ):
        """Init s3."""
        if default_template is None:
            default_template = {}

        self.region_name = region_name
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.config = AioConfig(signature_version="s3v4")

        self.project_name = project
        self.bucket_name = bucket
        # self.bucket = self.s3res.Bucket(bucket)
        self.default_template = default_template
        self.query_max_limit = query_max_limit

    @asynccontextmanager
    async def s3cli(self) -> AsyncGenerator[S3Client, None]:
        """创建客户端."""
        session = aioboto3.Session()
        async with session.client(
            "s3",
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            config=self.config,
        ) as s3cli:
            yield s3cli

    @staticmethod
    def encode_matedata(data: Dict[str, str]):
        """Encode matedata."""
        return {
            key: base64.b64encode(val.encode("utf8")).decode("utf8")
            for key, val in data.items()
        }

    @staticmethod
    def decode_matedata(data: Dict[str, str]):
        """Decode matedata."""

        def decode(val: str):
            try:
                return base64.b64decode(val.encode("utf8")).decode("utf8")
            except Exception:
                return val

        return {key: decode(val) for key, val in data.items()}

    def make_template_key(
        self, tid: Optional[str] = None, project: Optional[str] = None
    ):
        """Make template key."""
        if not project:
            project = self.project_name

        if tid:
            return "/".join([self.TEMPLATES_PREFIX, project, tid])
        else:
            return "/".join([self.TEMPLATES_PREFIX, project])

    async def clear_bucket(self):
        """Clear bucket."""
        r = await self.is_bucket_exist()
        if not r:
            await self.create_bucket_when_not_exist()
            return

        async with self.s3cli() as client:
            rrr = await client.list_object_versions(Bucket=self.bucket_name)
            if rrr.get("Versions", []):
                await client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={
                        "Objects": [
                            {"Key": i["Key"], "VersionId": i["VersionId"]}
                            for i in rrr.get("Versions", [])
                        ],
                    },
                )

            rrr = await client.list_objects_v2(Bucket=self.bucket_name)
            if rrr.get("Contents", []):
                await client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={
                        "Objects": [
                            {"Key": i["Key"], "VersionId": ""}
                            for i in rrr.get("Contents", [])
                        ],
                    },
                )
            await client.delete_bucket(Bucket=self.bucket_name)

    async def reset_bucket(self):
        """Delete bucket and Create bucket, Use for testing."""
        await self.clear_bucket()
        await self.create_bucket_when_not_exist()

    async def create_bucket_when_not_exist(self):
        """Create bucket when not exist."""
        if getattr(self, "has_bucket", False):
            return

        r = self.is_bucket_exist()
        if not r:
            await self.enable_bucket_versioning()
            await self.enable_bucket_lifecycle()
            setattr(self, "has_bucket", True)
            return

        async with self.s3cli() as client:
            await client.create_bucket(Bucket=self.bucket_name)

        await self.enable_bucket_versioning()
        await self.enable_bucket_lifecycle()
        setattr(self, "has_bucket", True)

    async def enable_bucket_lifecycle(self):
        """Enable bucket Lifecycle."""
        # TAG - https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutBucketLifecycleConfiguration.html#API_PutBucketLifecycleConfiguration_Examples
        if self.is_bucket_lifecycle_exist():
            return

        async with self.s3cli() as client:
            res = await client.put_bucket_lifecycle_configuration(
                Bucket=self.bucket_name,
                LifecycleConfiguration={
                    "Rules": [
                        {
                            "ID": "ReviewFileTemplate",
                            "Status": "Enabled",
                            "Prefix": self.REVIEW_PREFIX + "/",
                            "NoncurrentVersionExpiration": {
                                "NoncurrentDays": 1,
                                "NewerNoncurrentVersions": 5,
                            },
                        },
                    ]
                },
            )
            if res and res.get("ResponseMetadata", {}).get("HTTPStatusCode", 0) != 200:
                raise S3ClientError(f"Enabled Lifecycle Error[{res}]")

    async def enable_bucket_versioning(self):
        """Enable bucket versioning."""
        if getattr(self, "has_bucket_versioning", False):
            return

        async with self.s3cli() as client:
            status = await client.get_bucket_versioning(Bucket=self.bucket_name)
            if status.get("Status", "") != "Enabled":
                res = await client.put_bucket_versioning(
                    Bucket=self.bucket_name,
                    VersioningConfiguration={
                        "MFADelete": "Disabled",
                        "Status": "Enabled",
                    },
                )
                if (
                    res
                    and res.get("ResponseMetadata", {}).get("HTTPStatusCode", 0) != 200
                ):
                    raise S3ClientError(f"Enabled BucketVersioning Error[{res}]")

            setattr(self, "has_bucket_versioning", True)

    async def is_bucket_lifecycle_exist(self, bucket_name=None):
        """Is bucket exist."""
        if bucket_name is None:
            bucket_name = self.bucket_name

        async with self.s3cli() as client:
            try:
                # await client.head_bucket(Bucket=bucket_name)
                await client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            except ClientError as ex:
                if ex.response.get("Error", {}).get("Code", "") in [
                    "404",
                    "NoSuchLifecycleConfiguration",
                ]:
                    return False
                raise
            else:
                return True

    async def is_bucket_exist(self, bucket_name: Optional[str] = None):
        """Is bucket exist."""
        if bucket_name is None:
            bucket_name = self.bucket_name

        async with self.s3cli() as client:
            try:
                await client.head_bucket(Bucket=bucket_name)
            except ClientError as ex:
                if ex.response.get("Error", {}).get("Code", "") == "404":
                    return False
                raise
            else:
                return True

    @hook_create_bucket_when_not_exist()
    async def _is_object_exist(self, object_key, version_id: Optional[str] = None):
        """Is bbject exist."""
        async with self.s3cli() as client:
            try:
                if version_id:
                    await client.head_object(
                        Bucket=self.bucket_name, Key=object_key, VersionId=version_id
                    )
                else:
                    await client.head_object(Bucket=self.bucket_name, Key=object_key)
            except ClientError as ex:
                if ex.response.get("Error", {}).get("Code", "") == "404":
                    return False
                raise
            else:
                return True

    @hook_create_bucket_when_not_exist()
    async def _get_templates_list(
        self,
        tid: Optional[str] = None,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
        template_name: Optional[str] = None,
        template_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[sa.TemplateInfo]:
        """Get templates list."""
        assert (
            (template_name or not template_name)
            and (version_id or not version_id)
            and (offset >= 0)
        )

        async with self.s3cli() as client:
            _id_prefix = self.make_template_key(project=project)
            r = await client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=_id_prefix, MaxKeys=limit
            )
            res = []
            for obj in r.get("Contents", []):
                head = await client.head_object(Bucket=self.bucket_name, Key=obj["Key"])
                tinfo = self.__conv_dict(obj, head)

                if (template_type and template_type != tinfo.template_type) or (
                    template_name and template_name != tinfo.template_name
                ):
                    continue

                res.append(tinfo)
            return res

    @classmethod
    def __conv_dict(
        cls,
        obj: Union[ObjectTypeDef, ObjectVersionTypeDef],
        head: HeadObjectOutputTypeDef,
    ):
        """Get Body."""
        assert "/" in obj.get("Key", "")
        return sa.TemplateInfo(
            **{
                "tid": str(obj.get("Key", "")).rsplit("/", maxsplit=1)[-1],
                "version_id": obj.get("VersionId", "") or head["VersionId"],
                "updated_at": head["LastModified"],
                **cls.decode_matedata(dict(head["Metadata"])),
            }
        )

    async def _get_templates_version_list(
        self,
        tid: str,
        project: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[sa.TemplateInfo]:
        """Get templates list."""
        assert offset >= 0

        async with self.s3cli() as client:
            _id_prefix = self.make_template_key(tid, project=project)
            r = await client.list_object_versions(
                Bucket=self.bucket_name, Prefix=_id_prefix, MaxKeys=limit
            )

            res = []
            for obj in r.get("Versions", []):
                head = await client.head_object(
                    Bucket=self.bucket_name,
                    Key=obj["Key"],
                    VersionId=obj.get("VersionId", ""),
                )
                tinfo = self.__conv_dict(obj, head)
                res.append(tinfo)
            return res

    @hook_create_bucket_when_not_exist()
    async def _put_templates(
        self,
        tid: str,
        template_name: str,
        template_type: str,
        report: dict,
        project: Optional[str] = None,
    ) -> sa.TemplatesIdInfo:
        """Put templates."""
        if not report:
            if self.default_template:
                report = self.default_template
            else:
                report = {}

        if not project:
            project = self.project_name

        object_key = self.make_template_key(tid, project)
        async with self.s3cli() as client:
            res = await client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=BytesIO(json.dumps(report, indent=2).encode()),
                ContentType="application/json",
                Metadata=self.encode_matedata(
                    {
                        "template_name": template_name,
                        "template_type": template_type,
                    }
                ),
            )
            if res.get("ResponseMetadata", {}).get("HTTPStatusCode", "") != 200:
                raise S3ClientError(f"Save Template File Error[{res}]")

            version_id = res["VersionId"]

            return sa.TemplatesIdInfo(
                tid=tid,
                version_id=version_id,
                project=project,
            )

    @hook_create_bucket_when_not_exist()
    @hook_object_not_exist()
    async def _get_template(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
    ) -> Optional[sa.TemplateConfigInfo]:
        """Get templates."""
        object_key = self.make_template_key(tid, project)

        async with self.s3cli() as client:
            if version_id:
                res = await client.get_object(
                    Bucket=self.bucket_name, Key=object_key, VersionId=version_id
                )
            else:
                res = await client.get_object(Bucket=self.bucket_name, Key=object_key)

            data = await res["Body"].read()
            body = json.loads(str(data.decode("utf8")))
            if not body and self.default_template:
                body = self.default_template

            return sa.TemplateConfigInfo(
                **{
                    "tid": tid,
                    "version_id": res["VersionId"],
                    "updated_at": res["LastModified"],
                    **self.decode_matedata(res["Metadata"]),
                    "report": body,
                }
            )

    @hook_create_bucket_when_not_exist()
    async def _delete_template(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
    ):
        """Delete templates version."""
        async with self.s3cli() as client:
            if version_id:
                object_key = self.make_template_key(tid, project)
                delete_list = [(object_key, version_id)]
            else:
                delete_list = [
                    (self.make_template_key(i.tid, project), i.version_id)
                    for i in await self._get_templates_version_list(
                        tid, project=project, limit=10000
                    )
                ]

            await client.delete_objects(
                Bucket=self.bucket_name,
                Delete={
                    "Objects": [
                        {"Key": object_key, "VersionId": version_id}
                        for object_key, version_id in delete_list
                    ],
                },
            )


#     # ----------------------------------------------
#     #        代码段描述
#     # ----------------------------------------------

#     def make_review_key(self, file_surfix, project: Optional[str] = None):
#         """Make review key."""
#         self.create_bucket_when_not_exist()
#         if not project:
#             project = self.project_name
#         return "/".join([self.REVIEW_PREFIX, project, file_surfix])

#     def put_review(
#         self,
#         file_surfix: str,
#         file_buffer: bytes,
#         filename: str,
#         project: Optional[str] = None,
#     ) -> dict:
#         """Put templates."""
#         self.create_bucket_when_not_exist()
#         if file_surfix == "pdf":
#             ctx = "application/pdf"
#         elif file_surfix == "xlsx":
#             ctx = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         else:
#             raise S3ClientError(f"file_surfix invaild[{file_surfix}]")

#         object_key = self.make_review_key(file_surfix, project)
#         res = self.bucket.Object(object_key).put(
#             Body=BytesIO(file_buffer),
#             ContentType=ctx,
#             Metadata=self.encode_matedata(
#                 {
#                     "filename": filename,
#                 }
#             ),
#         )
#         if res.get("ResponseMetadata", {}).get("HTTPStatusCode", "") != 200:
#             raise S3ClientError(f"Save Template File Error[{res}]")

#         return {
#             "object_key": object_key,
#             "version_id": res["VersionId"],
#         }

#     def get_review(
#         self,
#         file_surfix: str,
#         version_id: str,
#         project: Optional[str] = None,
#     ) -> dict:
#         """Put templates."""
#         self.create_bucket_when_not_exist()
#         object_key = self.make_review_key(file_surfix, project)
#         obj = self.bucket.Object(object_key)
#         res = obj.get(VersionId=version_id)

#         if res.get("ResponseMetadata", {}).get("HTTPStatusCode", "") != 200:
#             raise S3ClientError(f"Save Template File Error[{res}]")

#         mdata = self.decode_matedata(res["Metadata"])

#         return {
#             "object_key": object_key,
#             "filename": mdata["filename"],
#             "data": res["Body"].read(),
#         }


class S3Backend(S3BackendClient, BackendBase):
    """S3Backend."""

    TEMPLATES_PREFIX = "templates"
    REVIEW_PREFIX = "review"

    async def clean_all(self):
        """Clean database, This api only use for test."""
        await self.clear_bucket()

    async def is_template_exist(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
    ) -> bool:
        """Is templates Exist."""
        object_id = self.make_template_key(tid, project)
        r = await self._is_object_exist(object_id, version_id)
        return r

    async def get_templates_list(
        self,
        tid: Optional[str] = None,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
        template_name: Optional[str] = None,
        template_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[sa.TemplateInfo]:
        """Get templates list."""
        r = await self._get_templates_list(
            tid, version_id, project, template_name, template_type, limit, offset
        )
        return r

    async def get_templates_version_list(
        self,
        tid: str,
        project: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[sa.TemplateInfo]:
        """Get templates version list."""
        r = await self._get_templates_version_list(tid, project, limit, offset)
        return r

    async def get_template(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
    ) -> Optional[sa.TemplateConfigInfo]:
        """Get templates."""
        r = await self._get_template(tid, version_id, project)
        return r

    async def put_template(
        self,
        template_name: str,
        template_type: str,
        report: dict,
        tid: Optional[str] = None,
        project: Optional[str] = None,
    ) -> sa.TemplatesIdInfo:
        """Put templates."""
        if tid is None:
            tid = await self.gen_uuid_object_key(project)

        r = await self._put_templates(
            tid, template_name, template_type, report, project
        )
        return r

    async def delete_template(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project: Optional[str] = None,
    ):
        """Delete templates version."""
        r = await self._delete_template(tid, version_id, project)
        return r
