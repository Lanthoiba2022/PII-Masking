# PII-Masking





## 🏗️ System Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React.js      │    │   FastAPI        │    │   AI Engines    │
│   Frontend      │◄──►│   Backend        │◄──►│                 │
│                 │    │                  │    │ • easyOCR       │
│ • File Upload   │    │ • ImageProcessing│    │ • Presidio      │
│ • Live Preview  │    │ • PII Detection  │    │ • spaCy NER     │
│ • Results View  │    │ • Privacy Masking│    │ • Custom Regex  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

# 📌 PII Guardian Frontend

This is the frontend for **PII Guardian**, a privacy-focused application that automatically detects and masks Personally Identifiable Information (PII) in images.  
---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/PII-Masking.git

cd frontend

npm install

npm run dev

By default, Vite will serve the frontend on:
👉 http://localhost:5173




# PII Guardian Backend (FastAPI)

FastAPI service that detects and masks PII from ID document images using OCR (EasyOCR), Presidio + spaCy NER, and regex heuristics. Masking is applied with OpenCV.

## Features
- Upload an image and receive a masked image (PNG)
- Optional JSON response with base64 image and detection metadata
- Dedicated detection endpoint (no image returned)
- CORS enabled for local frontend development
- Configurable mask style: black box or blur

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows PowerShell
```

2. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

3. (Optional, improves NER accuracy) Download a spaCy model:
```bash
python -m spacy download en_core_web_md
# or smaller:
python -m spacy download en_core_web_sm
```

## Run
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
```

Docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API

- `GET /health` → `{ "status": "ok" }`
- `POST /detect` (multipart: `file`) → `{ detected_pii: [{ entity_type, text, confidence, coordinates }] }`
- `POST /mask` (multipart: `file`)
  - Query params:
    - `style`: `box` (default) or `blur`
    - `as_json`: `false` to get raw PNG; `true` for JSON + base64
    - `min_confidence`: float [0,1]

Example to get detections only:
```bash
curl -s -X POST "http://localhost:8000/detect" -F "file=@/path/to/image.jpg" | jq .detected_pii
```

Example to get masked PNG:
```bash
curl -s -X POST "http://localhost:8000/mask?style=box" -F "file=@/path/to/image.jpg" --output masked.png
```

## Configuration
- `CORS_ORIGINS`: comma-separated list of allowed origins

## Notes
- First EasyOCR usage downloads weights; spaCy model download is optional but recommended.
- Custom Aadhaar recognizer is registered in `backend/app/presidio_engine.py`.
- Regex heuristics complement NER to capture Indian formats like Aadhaar and phone numbers. 