import os
import uuid
import shutil
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse

import extractor as paddle_extractor
import extractor_glm as glm_extractor

UPLOAD_DIR = Path("/tmp/ocr_uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".pdf"}
DEFAULT_ENGINE = os.getenv("DEFAULT_OCR_ENGINE", "paddle")


@asynccontextmanager
async def lifespan(app: FastAPI):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="OCR Service", version="1.0.0", lifespan=lifespan)


@app.post("/extract")
async def extract(
    file: UploadFile = File(...),
    engine: Literal["paddle", "glm"] = Query(default=DEFAULT_ENGINE, description="OCR engine: 'paddle' (PaddleOCR) or 'glm' (GLM-OCR via Ollama)"),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    tmp_path = UPLOAD_DIR / f"{uuid.uuid4()}{ext}"
    try:
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        if engine == "glm":
            blocks = glm_extractor.extract_text(str(tmp_path))
        else:
            blocks = paddle_extractor.extract_text(str(tmp_path))

        return JSONResponse({"filename": file.filename, "engine": engine, "blocks": blocks})
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@app.get("/health")
def health():
    return {"status": "ok", "default_engine": DEFAULT_ENGINE}
