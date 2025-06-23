import os
import re
from datetime import datetime

def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)

def generate_new_name(old_path: str, meta: dict) -> str:
    """
    Build a filename: YYYYMMDD_HHMMSS–first-30chars-of-text.ext
    """
    ext = os.path.splitext(old_path)[1]
    ts = meta.get("timestamp", datetime.utcnow().isoformat())
    dt = datetime.fromisoformat(ts)
    base = slugify(meta.get("text", ""))[:30] or dt.strftime("%H%M%S")
    return f"{dt.strftime('%Y%m%d_%H%M%S')}-{base}{ext}"
