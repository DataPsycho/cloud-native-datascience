import dataclasses
import typing as t

from microkit.datamodel import BaseDataModel


# Data Serializer for Project
@dataclasses.dataclass
class Job(BaseDataModel):
    """In memory metadata store when querying mongodb"""
    pid: t.Optional[str] = None
    entity_type: t.Optional[str] = None
    version: t.Optional[str] = None
    requested_by: t.Optional[str] = None
    requested_at: t.Optional[str] = None
    jid: t.Optional[str] = None
    name: t.Optional[str] = None
    finished_at: t.Optional[str] = None
    parent_entity_type: t.Optional[str] = None
    version_pointer: t.Optional[str] = None
    bucket: t.Optional[str] = None
    bucket_key: t.Optional[str] = None
    status: t.Optional[str] = None
    parent_entity_pid: t.Optional[str] = None
    status_jid: t.Optional[str] = None
    run: t.Optional[int] = None
