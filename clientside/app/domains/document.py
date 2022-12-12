import typing as t

from pydantic import BaseModel


class PostEnglishDocPayload(BaseModel):
    sk: str
    doc: str
    data: str
    updated_by: t.Optional[str] = "pluto"


class GetDocumentStatusPayload(BaseModel):
    pid: str


class GetGermanDocumentPayload(BaseModel):
    pid: str
    version: t.Optional[str] = "latest"


class GetGermanDocumentResult(BaseModel):
    content: str
    query: dict



