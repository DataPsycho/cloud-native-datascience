import abc
import dataclasses
import typing as t


@dataclasses.dataclass
class BaseDataModel(abc.ABC):
    PK: t.Optional[str]
    SK: t.Optional[str]

    @classmethod
    def from_dict(cls, d):
        """create self from a dictionary"""
        return cls(**d)

    def to_dict(self):
        """Convert itself to a dictionary"""
        return dataclasses.asdict(self)

