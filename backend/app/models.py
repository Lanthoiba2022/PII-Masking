from typing import List, Literal, Optional, Sequence, Tuple

from pydantic import BaseModel


class Detection(BaseModel):
    box: Sequence[Tuple[int, int]]
    text: str
    score: float
    types: List[str]


class MaskResponse(BaseModel):
    content_type: Literal["image/png", "image/jpeg"]
    image_base64: str
    masked_count: int
    detections: List[Detection] 