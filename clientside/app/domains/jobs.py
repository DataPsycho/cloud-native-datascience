import typing as t

from pydantic import BaseModel


class TranslationJob(BaseModel):
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


class GetJobStatusPayload(BaseModel):
    pid: str
    status: t.Optional[str] = "all"


class PostJobPayload(BaseModel):
    sk: str
    requested_by: t.Optional[str] = "pluto"
