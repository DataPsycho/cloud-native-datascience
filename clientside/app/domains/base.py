from __future__ import annotations

import abc
import dataclasses
import typing as t
from dataclasses import field


@dataclasses.dataclass
class BaseDataModel(abc.ABC):
    PK: t.Optional[str]
    SK: t.Optional[str]

    @classmethod
    def from_dict(cls, d: dict) -> BaseDataModel:
        """create self from a dictionary"""
        return cls(**d)

    def to_dict(self) -> dict:
        """Convert itself to a dictionary"""
        return dataclasses.asdict(self)


@dataclasses.dataclass
class BasePayloadModel(abc.ABC):
    field_schema: t.ClassVar[t.Dict] = field(default=False, init=False)  # type: ignore

    @classmethod
    def from_dict(cls, d: dict) -> BasePayloadModel:
        """Construct Self from dictionary"""
        raise NotImplementedError

    def to_dict(self) -> dict:
        """Convert itself to a dictionary"""
        return dataclasses.asdict(self)

    def field_ok(self) -> t.Tuple[bool, str]:
        data = self.__dict__
        missing_fields = []
        generic_text = (
            "Following field/fields must be provided: **{}**. "
            "\n\n*Or you have not confirm the request after you fill up the form. "
            "this is a generic message only applied in case there is a confirm button and you "
            "forget to confirm before submitting the request*."
        )
        if self.field_schema:
            for key, value in self.field_schema.items():  # type: ignore
                if value["required"]:
                    field_key = data.get(key)
                    if isinstance(field_key, bool) or isinstance(field_key, int) or isinstance(field_key, float):
                        field_key = str(field_key)
                    if field_key == '---' or not field_key or len(field_key) == 0:  # type: ignore
                        missing_fields.append(value["display_name"])

        if len(missing_fields) > 0:
            return False, generic_text.format(", ".join(missing_fields))
        return True, "OK"
