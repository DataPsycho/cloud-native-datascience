import typing as t

from pydantic import BaseModel


class PostProjectPayload(BaseModel):
    """Dataclass to store the user input for attr module"""
    name: str
    updated_by: t.Optional[str] = "pluto"


class Project(BaseModel):
    """In memory metadata store when querying mongodb"""
    PK: str
    SK: str
    name: str
    updated_by: str
    updated_at: str
    parent_entity_type: t.Optional[str] = "proj"
    entity_type: t.Optional[str] = 'project'
    document: t.Optional[str] = None
    bucket: t.Optional[str] = None
    bucket_key: t.Optional[str] = None
    active: t.Optional[bool] = True

