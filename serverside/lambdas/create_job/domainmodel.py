import dataclasses
import os
import typing as t
from uuid import uuid4

from microkit.datamodel import BaseDataModel
from microkit.utils import collect_cet_now, convert_to_internal_convention


# Data Serializer for Project
@dataclasses.dataclass
class Job(BaseDataModel):
    """In memory metadata store when querying mongodb"""
    pid: str
    entity_type: str
    version: str
    requested_by: str
    requested_at: str
    jid: t.Optional[str] = None
    name: t.Optional[str] = None
    finished_at: t.Optional[str] = None
    parent_entity_type: t.Optional[str] = "job"
    version_pointer: t.Optional[str] = None
    bucket: t.Optional[str] = None
    bucket_key: t.Optional[str] = None
    status: t.Optional[str] = "running"
    parent_entity_pid: t.Optional[str] = None
    status_jid: t.Optional[str] = None
    run: t.Optional[int] = None

    def __post_init__(self):
        if self.jid is None:
            self.jid = str(uuid4())
        if self.name is None:
            self.name = f"{self.entity_type} {self.version} {self.pid}"
        if self.PK is None:
            self.PK = f"proj#{self.pid}"
        if self.SK is None:
            self.SK = f"{self.entity_type}#{self.version}"
        if self.version_pointer is None:
            self.version_pointer = self.version
        self.bucket = os.environ["BUCKET"]
        self.bucket_key = self.create_bucket_key()
        self.version_pointer = self.version
        self.parent_entity_pid = f"{self.parent_entity_type}#{self.pid}"
        self.status_jid = f"{self.status}#{self.jid}"

    @classmethod
    def from_attribute_data(cls, pid, entity_type, version, requested_by):
        """Create it self from given set of attribute"""
        PK = None
        SK = None
        return cls(
            PK=PK,
            SK=SK,
            pid=pid,
            entity_type=entity_type,
            version=version,
            requested_by=requested_by,
            requested_at=collect_cet_now(),

        )

    @classmethod
    def from_v0(cls, pid: str, entity_type: str):
        """Create the version 0 from viven project id and entity type"""
        pk = None
        sk = None
        return cls(
            PK=pk,
            SK=sk,
            pid=pid,
            entity_type=entity_type,
            requested_by="unknown",
            requested_at=collect_cet_now(),
            version="v0"
        )

    def create_bucket_key(self):
        project_path = self.pid.replace('_', '-').replace(':', '-')
        return os.path.join(self.parent_entity_type, project_path, self.entity_type, self.version)

    def set_run(self, value: int) -> None:
        """Setter for the run data attribute"""
        self.run = value

    def set_requested_by(self, requested_by: str) -> None:
        """Setter for the requested_by attribute"""
        self.requested_by = requested_by

    def get_s3_path(self):
        return f"s3://{self.bucket}/{self.bucket_key}"


@dataclasses.dataclass
class ExecutonSchemaJob:
    SOURCE_TO_TRANSLATE: str
    DESTINATION_OUTPUT: str
    SOURCE_MODEL_ARTIFACT: str
    job_pk: str
    job_sk: str
    input_code: str
    ProcessingJobName: t.Optional[str] = None
    NAME_PREFIX = "ProcessingJobTranslate"

    def __post_init__(self):
        if self.ProcessingJobName is None:
            self.ProcessingJobName = f"{self.NAME_PREFIX}-{str(uuid4())}"
        self.input_code = os.path.join(self.input_code, "main.py")

    @classmethod
    def from_dict(self, d):
        """create self from a dictionary"""
        return self(**d)

    def to_dict(self):
        """Convert itself to a dictionary"""
        return dataclasses.asdict(self)

    def reset_job_name(self, suffix: str):
        "Reset the job name with a uuid prefrably"
        self.ProcessingJobName = f"{self.NAME_PREFIX}-{suffix}"


@dataclasses.dataclass
class Project(BaseDataModel):
    """In memory metadata store when querying mongodb"""
    name: str
    updated_by: str
    updated_at: str
    parent_entity_type: t.Optional[str] = "proj"
    entity_type: t.Optional[str] = 'project'
    document: t.Optional[str] = None
    bucket: t.Optional[str] = None
    bucket_key: t.Optional[str] = None
    active: t.Optional[bool] = True

    def __post_init__(self):
        self.name = convert_to_internal_convention(self.name)
        if self.PK is None:
            self.PK = f"{self.parent_entity_type}#{self.entity_type}"
        if self.SK is None:
            self.SK = f"{self.name}-{self.updated_at}"

    @classmethod
    def from_attribute_data(
        cls,
        name: str,
        updated_by: str,
        updated_at: str
    ):
        PK = None
        SK = None
        return cls(
            PK=PK,
            SK=SK,
            name=name,
            updated_by=updated_by,
            updated_at=updated_at
        )

    @classmethod
    def from_sk(cls, sk: str):
        return cls(PK=None, SK=sk, name="Unknown", updated_by="unknown", updated_at=collect_cet_now())

    def create_sort_key(self):
        sk_name = convert_to_internal_convention(self.name)
        timestamp = collect_cet_now()
        return f"{sk_name}_{timestamp}"

    def set_doc(self, filename: str) -> None:
        self.document = filename

    def set_bucket(self, bucket: str) -> None:
        self.bucket = bucket

    def set_bucket_key(self, bucket_key: str) -> None:
        self.bucket_key = bucket_key

    def set_updated_by(self, updated_by: str) -> None:
        self.updated_by = updated_by

    def set_updated_at(self) -> None:
        self.updated_at = collect_cet_now()

