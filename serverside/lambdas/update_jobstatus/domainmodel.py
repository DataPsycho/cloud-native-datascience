import dataclasses
import os
import typing as t
from uuid import uuid4

from microkit.datamodel import BaseDataModel
from microkit.utils import collect_cet_now


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
        self.bucket = os.environ["BUCKET"]
        self.bucket_key = self.create_bucket_key()
        if self.version_pointer is None:
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

    @classmethod
    def from_keys(cls, pk: str, sk: str):
        pid = pk.replace("proj#", "")
        entity_type, version = sk.split("#")
        return cls(
            PK=pk,
            SK=sk,
            pid=pid,
            entity_type=entity_type,
            version=version,
            requested_by="unknown",
            requested_at=collect_cet_now()
        )

    def set_run(self, value: int) -> None:
        """Setter for the run data attribute"""
        self.run = value

    def create_bucket_key(self):
        project_path = self.pid.replace('_', '-').replace(':', '-')
        return os.path.join(self.parent_entity_type, project_path, self.entity_type, self.version)

    def set_requested_by(self, requested_by: str) -> None:
        """Setter for the requested_by attribute"""
        self.requested_by = requested_by

    def get_s3_path(self):
        return f"s3://{self.bucket}/{self.bucket_key}"

    def get_config_path(self):
        return f"{self.get_s3_path()}/config"
