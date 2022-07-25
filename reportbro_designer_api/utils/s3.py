# -*- coding: utf-8 -*-
"""
@create: 2022-07-22 17:54:46.

@author: ppolxda

@desc: S3 Api
"""
import json
from io import BytesIO
from typing import List
from typing import Optional
from uuid import uuid1

import boto3
import shortuuid
from botocore.client import ClientError
from botocore.client import Config

from reportbro_designer_api.errors import S3ClientError


class ReportbroS3Client(object):
    """ReportbroS3Client."""

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
    ):
        """Init s3."""
        if default_template is None:
            default_template = {}

        self.s3cli = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name=region_name,
        )
        self.s3res = boto3.resource(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name=region_name,
        )
        self.project_name = project
        self.bucket_name = bucket
        self.bucket = self.s3res.Bucket(bucket)
        self.default_template = default_template

    def make_template_key(self, object_id="", project=None):
        """Make template key."""
        if not project:
            project = self.project_name
        return "/".join([self.TEMPLATES_PREFIX, project, object_id])

    def reset_bucket(self):
        """Delete bucket and Create bucket, Use for testing."""
        if not self.is_bucket_exist():
            self.create_bucket_when_not_exist()
            return

        for i in self.bucket.object_versions.all():
            i.delete()

        for i in self.bucket.objects.all():
            i.delete()

        self.bucket.delete()
        self.create_bucket_when_not_exist()

    def create_bucket_when_not_exist(self):
        """Create bucket when not exist."""
        if getattr(self, "has_bucket", False):
            return

        if self.is_bucket_exist():
            self.enable_bucket_versioning()
            self.enable_bucket_lifecycle()
            setattr(self, "has_bucket", True)
            return

        self.bucket.create(ACL="public-read")
        self.enable_bucket_versioning()
        self.enable_bucket_lifecycle()
        setattr(self, "has_bucket", True)

    def enable_bucket_lifecycle(self):
        """Enable bucket Lifecycle."""
        # TAG - https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutBucketLifecycleConfiguration.html#API_PutBucketLifecycleConfiguration_Examples
        if self.is_bucket_lifecycle_exist():
            return

        self.bucket.Lifecycle().put(
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
            }
        )

    def enable_bucket_versioning(self):
        """Enable bucket versioning."""
        if getattr(self, "has_bucket_versioning", False):
            return

        if not self.s3res.BucketVersioning(self.bucket_name).status:
            self.s3res.BucketVersioning(self.bucket_name).enable()

        setattr(self, "has_bucket_versioning", True)

    def is_bucket_lifecycle_exist(self, bucket_name=None):
        """Is bucket exist."""
        if bucket_name is None:
            bucket_name = self.bucket.name

        try:
            self.s3cli.head_bucket(Bucket=bucket_name)
            self.bucket.Lifecycle().load()
        except ClientError as ex:
            if ex.response.get("Error", {}).get("Code", "") in [
                "404",
                "NoSuchLifecycleConfiguration",
            ]:
                return False
            raise
        else:
            return True

    def is_bucket_exist(self, bucket_name=None):
        """Is bucket exist."""
        if bucket_name is None:
            bucket_name = self.bucket.name

        try:
            self.s3cli.head_bucket(Bucket=bucket_name)
        except ClientError as ex:
            if ex.response.get("Error", {}).get("Code", "") == "404":
                return False
            raise
        else:
            return True

    def is_object_exist(self, object_key):
        """Is bucket exist."""
        self.create_bucket_when_not_exist()
        try:
            self.bucket.Object(object_key).load()
        except ClientError as ex:
            if ex.response.get("Error", {}).get("Code", "") == "404":
                return False
            raise
        else:
            return True

    def gen_uuid_object_key(self, project=None) -> str:
        """Generate uuid."""
        self.create_bucket_when_not_exist()
        _id = str(shortuuid.encode(uuid1()))
        object_key = self.make_template_key(_id, project=project)
        if self.is_object_exist(object_key):
            return self.gen_uuid_object_key()
        return _id

    def get_templates_list(
        self, template_type: Optional[str] = None, project=None
    ) -> list:
        """Get templates list."""
        self.create_bucket_when_not_exist()

        def conv_dict(version, obj):
            """Get Body."""
            assert "/" in version.key
            assert version.key == obj.key
            return {
                "tid": str(version.key).rsplit("/", maxsplit=1)[-1],
                "version_id": obj.version_id,
                **obj.metadata,
            }

        if template_type:
            filter_type = lambda x: x["report"] == template_type
        else:
            filter_type = lambda x: x

        _id_prefix = self.make_template_key(project=project)
        return list(
            filter(
                filter_type,
                map(
                    lambda obj: conv_dict(obj, self.bucket.Object(obj.key)),
                    self.bucket.objects.filter(Prefix=_id_prefix),
                ),
            )
        )

    def put_templates(
        self,
        tid: str,
        template_name: str,
        template_type: str,
        report: dict,
        project=None,
    ) -> dict:
        """Put templates."""
        self.create_bucket_when_not_exist()
        if not report:
            if self.default_template:
                report = self.default_template
            else:
                report = {}

        object_key = self.make_template_key(tid, project)
        res = self.bucket.Object(object_key).put(
            Body=BytesIO(json.dumps(report, indent=2).encode()),
            ContentType="application/json",
            Metadata={
                "template_name": template_name,
                "template_type": template_type,
            },
        )
        if res.get("ResponseMetadata", {}).get("HTTPStatusCode", "") != 200:
            raise S3ClientError(f"Save Template File Error[{res}]")

        return {
            "tid": tid,
            "version_id": res["VersionId"],
        }

    def get_templates_object(
        self,
        tid: str,
        project=None,
    ):
        """Get templates."""
        self.create_bucket_when_not_exist()
        object_key = self.make_template_key(tid, project)
        obj = self.bucket.Object(object_key)
        return obj

    def get_templates(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project=None,
    ) -> dict:
        """Get templates."""
        self.create_bucket_when_not_exist()
        object_key = self.make_template_key(tid, project)
        obj = self.bucket.Object(object_key)

        if version_id:
            res = obj.get(VersionId=version_id)
        else:
            res = obj.get()

        if res.get("ResponseMetadata", {}).get("HTTPStatusCode", "") != 200:
            raise S3ClientError(f"Save Template File Error[{res}]")

        body = json.loads(res["Body"].read())
        if not body and self.default_template:
            body = self.default_template

        return {
            "tid": object_key,
            "version_id": res["VersionId"],
            **res["Metadata"],
            "template_body": body,
        }

    def get_templates_version_list(
        self,
        tid: str,
        project=None,
    ) -> List[dict]:
        """Get templates version list."""
        self.create_bucket_when_not_exist()
        object_key = self.make_template_key(tid, project)

        def conv_dict(version, obj):
            """Get Body."""
            assert "/" in version.key
            assert version.key == obj.key
            return {
                "tid": str(version.key).rsplit("/", maxsplit=1)[-1],
                "version_id": version.version_id,
                **obj.metadata,
            }

        return [
            conv_dict(obj, self.bucket.Object(obj.key))
            for obj in self.bucket.object_versions.filter(Prefix=object_key)
        ]

    def delete_templates_version(
        self,
        tid: str,
        version_id: Optional[str] = None,
        project=None,
    ):
        """Delete templates version."""
        self.create_bucket_when_not_exist()

        if version_id:
            object_key = self.make_template_key(tid, project)
            delete_list = [(object_key, version_id)]
        else:
            delete_list = [
                (self.make_template_key(i["tid"], project), i["version_id"])
                for i in self.get_templates_version_list(tid, project=project)
            ]

        self.bucket.delete_objects(
            Delete={
                "Objects": [
                    {"Key": object_key, "VersionId": version_id}
                    for object_key, version_id in delete_list
                ],
            },
        )

    # ----------------------------------------------
    #        代码段描述
    # ----------------------------------------------

    def make_review_key(self, file_surfix, project=None):
        """Make review key."""
        self.create_bucket_when_not_exist()
        if not project:
            project = self.project_name
        return "/".join([self.REVIEW_PREFIX, project, file_surfix])

    def put_review(
        self,
        file_surfix: str,
        file_buffer: bytes,
        filename: str,
        project=None,
    ) -> dict:
        """Put templates."""
        self.create_bucket_when_not_exist()
        if file_surfix == "pdf":
            ctx = "application/pdf"
        elif file_surfix == "xlsx":
            ctx = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            raise S3ClientError(f"file_surfix invaild[{file_surfix}]")

        object_key = self.make_review_key(file_surfix, project)
        res = self.bucket.Object(object_key).put(
            Body=BytesIO(file_buffer),
            ContentType=ctx,
            Metadata={
                "filename": filename,
            },
        )
        if res.get("ResponseMetadata", {}).get("HTTPStatusCode", "") != 200:
            raise S3ClientError(f"Save Template File Error[{res}]")

        return {
            "object_key": object_key,
            "version_id": res["VersionId"],
        }

    def get_review(
        self,
        file_surfix: str,
        version_id: str,
        project=None,
    ) -> dict:
        """Put templates."""
        self.create_bucket_when_not_exist()
        object_key = self.make_review_key(file_surfix, project)
        obj = self.bucket.Object(object_key)
        res = obj.get(VersionId=version_id)

        if res.get("ResponseMetadata", {}).get("HTTPStatusCode", "") != 200:
            raise S3ClientError(f"Save Template File Error[{res}]")

        return {
            "object_key": object_key,
            "filename": res["Metadata"]["filename"],
            "data": res["Body"].read(),
        }
