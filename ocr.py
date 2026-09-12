"""
ocr.py — Image-based medicine identification (Owner: Faiza)

CONTRACT (do not change without telling the whole team):
    identify_from_image(image) -> {
        "medicine_name": str | None,
        "confidence": float   # 0.0 - 1.0
    }

CURRENT STATE: uses pytesseract for text extraction, then fuzzy-matches
extracted text against the known medicine list. Requires Tesseract OCR
installed on the system (not just the pip package):
    - Mac:   brew install tesseract
    - Ubuntu: sudo apt-get install tesseract-ocr
    - pip:   pip install pytesseract pillow

TODO (Faiza):
    1. Test against real, imperfect photos (blurry, angled, poor lighting) —
       not just clean screenshots of text. TC-06 depends on this being honest
       about low confidence, not falsely confident.
    2. Tune the confidence threshold below (LOW_CONFIDENCE_THRESHOLD) based on
       real test results.
    3. If Tesseract accuracy is too poor on real photos, fall back to a cloud
       OCR API — flag this to the team early, not at hour 15.
"""

import csv
import os
from difflib import get_close_matches

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "medicines.csv")
LOW_CONFIDENCE_THRESHOLD = 0.5


def _load_medicine_names():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return [row["medicine_name"] for row in csv.DictReader(f)]


_MEDICINE_NAMES = _load_medicine_names()


def _extract_text(image) -> str:
    """Run OCR on the image. `image` can be a file path or a PIL Image."""
    if pytesseract is None:
        raise RuntimeError("pytesseract not installed — run: pip install pytesseract pillow")

    if isinstance(image, str):
        image = Image.open(image)

    return pytesseract.image_to_string(image)


def identify_from_image(image) -> dict:
    """
    Extract text from an uploaded image and match it against the known
    medicine list. Returns None/0.0 confidence if nothing usable is found —
    NEVER guess a name just to return something.
    """
    try:
        raw_text = _extract_text(image)
    except Exception:
        return {"medicine_name": None, "confidence": 0.0}

    if not raw_text.strip():
        return {"medicine_name": None, "confidence": 0.0}

    words = raw_text.split()
    best_match = None
    best_score = 0.0

    for word in words:
        matches = get_close_matches(word.lower(), [n.lower() for n in _MEDICINE_NAMES], n=1, cutoff=0.6)
        if matches:
            # crude confidence: exact-ish match length ratio
            score = len(matches[0]) / max(len(word), 1)
            score = min(score, 1.0)
            if score > best_score:
                best_score = score
                best_match = matches[0]

    if best_match is None:
        return {"medicine_name": None, "confidence": 0.0}

    for name in _MEDICINE_NAMES:
        if name.lower() == best_match:
            return {"medicine_name": name, "confidence": round(best_score, 2)}

    return {"medicine_name": None, "confidence": 0.0}


def is_low_confidence(result: dict) -> bool:
    """Helper for the UI layer to decide whether to show the uncertainty flag."""
    return result["confidence"] < LOW_CONFIDENCE_THRESHOLD or result["medicine_name"] is None


if __name__ == "__main__":
    # quick manual test — replace with a real image path to test locally
    # print(identify_from_image("sample_package.jpg"))
    print("Loaded", len(_MEDICINE_NAMES), "reference medicine names for matching.")
