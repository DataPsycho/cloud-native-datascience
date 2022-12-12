import dataclasses
import typing as t

from microkit.datamodel import BaseDataModel
from microkit.utils import convert_to_internal_convention, create_metacomposit


@dataclasses.dataclass
class Project(BaseDataModel):
    """In memory metadata store when querying mongodb"""
    franchise: str
    acting: str
    indication: str
    doctype: t.List
    updated_by: str
    updated_at: str
    study_name: t.Optional[str] = None
    qlephrase: t.Optional[str] = None
    name: t.Optional[str] = None
    parent_entity_type: t.Optional[str] = "proj"
    entity_type: t.Optional[str] = 'project'
    dossier: t.Optional[str] = None
    bucket: t.Optional[str] = None
    bucket_key: t.Optional[str] = None
    active: t.Optional[bool] = True
    project_meta_composit: t.Optional[str] = None

    def __post_init__(self):
        if self.name is None:
            self.name = self.create_project_name()
        if self.PK is None:
            self.PK = f"{self.parent_entity_type}#{self.entity_type}"
        if self.SK is None:
            self.SK = self.create_sort_key()
        if self.project_meta_composit is None:
            self.project_meta_composit = create_metacomposit([self.franchise, self.acting, self.indication, self.doctype])

    @classmethod
    def from_attribute_data(
        cls,
        franchise: str,
        acting: str,
        indication: str,
        doctype: str,
        study_name: str,
        qlephrase: str,
        updated_by: str,
        updated_at: str
    ):
        PK = None
        SK = None
        return cls(
            PK=PK,
            SK=SK,
            franchise=franchise,
            acting=acting,
            indication=indication,
            doctype=doctype,
            study_name=study_name,
            qlephrase=qlephrase,
            updated_by=updated_by,
            updated_at=updated_at
        )

    def create_sort_key(self):
        sk_name = convert_to_internal_convention(self.name)
        return f"{sk_name}-{self.updated_at}"

    def create_project_name(self) -> str:
        doc_type_text = "-".join(self.doctype).replace(" ", "")
        name = f"{self.acting} {self.indication} {doc_type_text}"
        return name
