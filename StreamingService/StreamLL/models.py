from pydantic import BaseModel
from enum import StrEnum

class CamType(StrEnum):
    CAMR1 = "camr1"
    CAML1 = "caml1"
    CAMR2 = "camr2"
    CAML2 = "caml2"

class StreamSettings(BaseModel):
    cam: CamType
    cam_path: str
    fps: int
    width: int
    height: int