from typing import Iterable, List, Sequence, Tuple

import numpy as np

Point = Tuple[int, int]


def _polygon_to_mask(image_shape: Sequence[int], polygon: Sequence[Point]) -> np.ndarray:
    import cv2  # lazy import
    mask = np.zeros(image_shape[:2], dtype=np.uint8)
    pts = np.array(polygon, dtype=np.int32)
    cv2.fillPoly(mask, [pts], 255)
    return mask


def mask_regions_with_box(image_bgr: np.ndarray, polygons: Iterable[Sequence[Point]], color: Tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
    import cv2  # lazy import
    result = image_bgr.copy()
    for poly in polygons:
        pts = np.array(poly, dtype=np.int32)
        cv2.fillPoly(result, [pts], color)
    return result


def mask_regions_with_blur(image_bgr: np.ndarray, polygons: Iterable[Sequence[Point]], ksize: int = 41) -> np.ndarray:
    import cv2  # lazy import
    if ksize % 2 == 0:
        ksize += 1
    blurred = cv2.GaussianBlur(image_bgr, (ksize, ksize), 0)
    result = image_bgr.copy()
    for poly in polygons:
        mask = _polygon_to_mask(image_bgr.shape, poly)
        result[mask == 255] = blurred[mask == 255]
    return result 