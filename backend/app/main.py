import base64
import io
from typing import Iterable, List, Sequence, Tuple

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse

from .image_utils import mask_regions_with_blur, mask_regions_with_box
from .models import Detection, MaskResponse
from .ocr import run_ocr
from .pii import pii_summary, should_mask, classify_text
from .settings import get_cors_origins
from .presidio_engine import analyze_texts


app = FastAPI(title="PII Guardian API", version="1.0.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=get_cors_origins(),
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.get("/health")
async def health():
	return {"status": "ok"}


@app.get("/")
async def root():
	return {"name": "PII Guardian API", "version": "1.0.0"}


def _load_image_to_bgr(data: bytes) -> np.ndarray:
	np_arr = np.frombuffer(data, dtype=np.uint8)
	img_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
	if img_bgr is None:
		raise ValueError("Unsupported image format or corrupted image")
	return img_bgr


def _map_regex_types_to_entities(types: List[str]) -> List[str]:
	mapped: List[str] = []
	for t in types:
		lt = t.lower()
		if lt == "email":
			mapped.append("EMAIL_ADDRESS")
		elif lt == "phone":
			mapped.append("PHONE_NUMBER")
		elif lt == "aadhaar":
			mapped.append("AADHAAR_NUMBER")
		elif lt == "dob":
			mapped.append("DATE_OF_BIRTH")
		elif lt == "name":
			mapped.append("PERSON")
		elif lt == "address":
			mapped.append("ADDRESS")
		else:
			mapped.append(t.upper())
	return list(dict.fromkeys(mapped))


@app.post("/detect")
async def detect_pii(
	file: UploadFile = File(..., description="Image file to analyze"),
	min_confidence: float = Query(0.3, ge=0.0, le=1.0),
):
	try:
		content = await file.read()
		image_bgr = _load_image_to_bgr(content)
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

	ocr_dets = run_ocr(image_bgr)
	texts = [d.get("text", "") for d in ocr_dets if d.get("score", 0.0) >= min_confidence]
	presidio_results = analyze_texts(texts)

	detected: List[dict] = []
	idx = 0
	for det in ocr_dets:
		if det.get("score", 0.0) < min_confidence:
			continue
		text = det.get("text", "").strip()
		regex_types = _map_regex_types_to_entities(classify_text(text))
		presidio_entities = presidio_results[idx] if idx < len(presidio_results) else []
		idx += 1

		all_types = set(regex_types + [e["entity_type"] for e in presidio_entities])
		for t in all_types:
			detected.append({
				"entity_type": t,
				"text": text,
				"confidence": float(det.get("score", 0.0)),
				"coordinates": det.get("box", []),
			})

	return {"detected_pii": detected}


@app.post("/mask")
async def mask_pii(
	file: UploadFile = File(..., description="Image file to process"),
	style: str = Query("box", description="Mask style: 'box' or 'blur'"),
	as_json: bool = Query(False, description="Return JSON with base64 instead of raw image"),
	min_confidence: float = Query(0.3, ge=0.0, le=1.0, description="Minimum OCR confidence to consider"),
):
	try:
		content = await file.read()
		image_bgr = _load_image_to_bgr(content)
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

	# OCR detections
	detections_raw = run_ocr(image_bgr)

	# Presidio analysis on texts above threshold
	texts = [d.get("text", "") for d in detections_raw if d.get("score", 0.0) >= min_confidence]
	presidio_results = analyze_texts(texts)

	# Filter detections to mask
	polygons_to_mask: List[Sequence[Tuple[int, int]]] = []
	detections: List[Detection] = []

	idx = 0
	for det in detections_raw:
		if det.get("score", 0.0) < min_confidence:
			continue
		text = det.get("text", "").strip()
		regex_types = _map_regex_types_to_entities(classify_text(text))
		presidio_entities = presidio_results[idx] if idx < len(presidio_results) else []
		idx += 1
		combined_types = list(dict.fromkeys(regex_types + [e["entity_type"] for e in presidio_entities]))
		if combined_types:
			polygons_to_mask.append(det["box"])  # type: ignore
		detections.append(Detection(
			box=det["box"],
			text=text,
			score=float(det.get("score", 0.0)),
			types=combined_types,
		))

	# Apply masking
	if style == "blur":
		masked_bgr = mask_regions_with_blur(image_bgr, polygons_to_mask)
	else:
		masked_bgr = mask_regions_with_box(image_bgr, polygons_to_mask)

	# Encode output
	success, encoded = cv2.imencode(".png", masked_bgr)
	if not success:
		raise HTTPException(status_code=500, detail="Failed to encode masked image")

	if as_json:
		b64 = base64.b64encode(encoded.tobytes()).decode("utf-8")
		return MaskResponse(
			content_type="image/png",
			image_base64=b64,
			masked_count=len(polygons_to_mask),
			detections=detections,
		)

	return Response(content=encoded.tobytes(), media_type="image/png") 