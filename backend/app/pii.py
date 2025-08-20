import re
from typing import Dict, List, Optional

# Common PII regexes (India-oriented with some general forms)
AADHAAR_REGEX = re.compile(r"\b(?:\d{4}\s?\d{4}\s?\d{4})\b")
PHONE_REGEX = re.compile(r"\b(?:\+?91[-\s]?)?[6-9]\d{9}\b")
DOB_REGEX = re.compile(r"\b(?:\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4})\b", re.IGNORECASE)
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# Heuristics for labels that indicate the line contains PII value(s)
LABEL_KEYWORDS = [
    "aadhaar", "uidai", "uid", "enrolment", "enrollment",
    "name", "s/o", "d/o", "w/o", "father", "mother",
    "dob", "date of birth", "year of birth",
    "address", "addr",
    "phone", "mobile", "contact",
    "email", "e-mail",
]

# Basic name heuristic: words with initials / proper case and length
NAME_HEURISTIC = re.compile(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def classify_text(text: str) -> List[str]:
    """
    Returns a list of PII types found in the text line.
    Possible types: ["aadhaar", "phone", "dob", "email", "address", "name", "labeled"]
    """
    t = text.lower()
    found: List[str] = []

    if AADHAAR_REGEX.search(text):
        found.append("aadhaar")
    if PHONE_REGEX.search(text):
        found.append("phone")
    if DOB_REGEX.search(text):
        found.append("dob")
    if EMAIL_REGEX.search(text):
        found.append("email")

    # Labels
    if any(k in t for k in LABEL_KEYWORDS):
        found.append("labeled")

    # Name/address heuristics (only if reasonably long words and not clearly non-text)
    if "address" in t or "addr" in t:
        found.append("address")
    else:
        # If the line looks like a proper name and is not just a single token
        if NAME_HEURISTIC.match(text.strip()):
            found.append("name")

    return list(dict.fromkeys(found))  # dedupe while preserving order


def should_mask(text: str) -> bool:
    return len(classify_text(text)) > 0


def pii_summary(text: str) -> Optional[Dict[str, List[str]]]:
    types = classify_text(text)
    if not types:
        return None
    return {"types": types} 