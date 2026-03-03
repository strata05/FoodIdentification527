from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException
import uuid, datetime as dt, shutil

"""
File upload utilities:

- Allow only jpg, jpeg, png, gif, webp.
- Generate save directories by user ID and date.
- Ensure the target directory exists (create if missing).
- Use UUIDs for unique filenames to avoid collisions.
- Save the file locally and return its path, size, and content type.
"""

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
UPLOAD_ROOT = Path("uploads")


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def _gen_target(u_id: str, original_name: str) -> tuple[Path, str]:
    ext = Path(original_name).suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    today = dt.date.today()
    sub = Path("user") / u_id / today.strftime("%Y/%m/%d")
    ensure_dir(UPLOAD_ROOT / sub)

    fname = f"{uuid.uuid4().hex}{ext}"
    rel_path = sub / fname  # Path object
    rel = rel_path.as_posix()  # convert to string format: e.g. 'user/.../xxx.png'

    return (UPLOAD_ROOT / rel_path), rel


def save_upload_file(u_id: str, f: UploadFile) -> Tuple[str, int, str]:
    target, rel = _gen_target(u_id, f.filename or "file")
    with target.open("wb") as w:
        shutil.copyfileobj(f.file, w)
    size = target.stat().st_size
    ctype = f.content_type or "application/octet-stream"
    return rel, size, ctype
