import pytesseract
from PIL import Image
import os
from datetime import datetime

def analyze_file(path: str) -> dict:
    """
    Run OCR and extract basic metadata (e.g. timestamp from EXIF or now).
    """
    # TODO: Add more sophisticated metadata extraction
    text = ""
    try:
        text = pytesseract.image_to_string(Image.open(path))
    except Exception:
        pass
    timestamp = datetime.utcnow().isoformat()
    return {"text": text, "timestamp": timestamp}
