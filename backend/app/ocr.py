from functools import lru_cache
from typing import Dict, List, Tuple

import numpy as np


@lru_cache(maxsize=1)
def _get_reader():
    # Import lazily so import time is fast and optional GPU setup is avoided.
    import easyocr  # type: ignore

    # Force CPU for broader compatibility
    return easyocr.Reader(["en"], gpu=False)


def run_ocr(image_bgr: np.ndarray) -> List[Dict]:
    """
    Runs OCR on a BGR image array and returns a list of detections.

    Each detection is a dict with:
      - box: List[Tuple[int, int]]  four-point polygon (x, y)
      - text: str
      - score: float
    """
    reader = _get_reader()
    # EasyOCR expects RGB
    image_rgb = image_bgr[:, :, ::-1]
    results = reader.readtext(image_rgb)

    detections: List[Dict] = []
    for item in results:
        box_pts, text, score = item
        box = [(int(pt[0]), int(pt[1])) for pt in box_pts]
        detections.append({
            "box": box,
            "text": text.strip(),
            "score": float(score),
        })
    return detections 