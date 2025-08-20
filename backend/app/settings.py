import os
from typing import List


def get_cors_origins() -> List[str]:
    # Default to common dev origins
    default_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    raw = os.getenv("CORS_ORIGINS", "")
    if not raw:
        return default_origins
    return [origin.strip() for origin in raw.split(",") if origin.strip()] 