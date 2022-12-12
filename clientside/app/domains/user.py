from pydantic import BaseModel


class GetUserPayload(BaseModel):
    """Dataclass to store the user input for attr module"""
    uid: str
    pin: str

