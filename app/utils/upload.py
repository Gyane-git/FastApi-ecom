import os
import re
import uuid

from fastapi import HTTPException, UploadFile

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
MAX_SIZE_BYTES = 10 * 1024 * 1024


async def save_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
    content = await file.read()
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", os.path.splitext(file.filename or "image")[0])[:50]
    filename = f"{safe_name}_{uuid.uuid4().hex[:8]}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(content)
    return f"/uploads/{filename}"
