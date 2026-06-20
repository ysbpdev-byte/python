import os
import uuid
import shutil
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from extractor import extract_text

UPLOAD_DIR = Path("/tmp/ocr_uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".pdf"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="OCR Service", version="1.0.0", lifespan=lifespan)


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    tmp_path = UPLOAD_DIR / f"{uuid.uuid4()}{ext}"
    try:
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        blocks = extract_text(str(tmp_path))
        return JSONResponse({"filename": file.filename, "blocks": blocks})
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@app.get("/health")
def health():
    return {"status": "ok"}
