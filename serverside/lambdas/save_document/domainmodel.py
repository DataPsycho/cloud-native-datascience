import dataclasses
import typing as t

from microkit.datamodel import BaseDataModel
from microkit.utils import collect_cet_now, convert_to_internal_convention


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

    def create_project_name(self) -> str:
        doc_type_text = "_".join(self.doctype).replace(" ", "")
        name = f"{self.acting} {self.indication} {doc_type_text}"
        return name

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
