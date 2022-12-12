import abc
import dataclasses


@dataclasses.dataclass
class BaseDataModel(abc.ABC):
    PK: str  # attr#entity_type
    SK: str  # id

    @classmethod
    def from_dict(self, d):
        """create self from a dictionary"""
        return self(**d)

    def to_dict(self):
        """Convert itself to a dictionary"""
        return dataclasses.asdict(self)

