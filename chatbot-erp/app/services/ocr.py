import os
import httpx
from dotenv import load_dotenv

load_dotenv()

OCR_URL = os.getenv("OCR_URL", "http://localhost:2006")
OCR_ENGINE = os.getenv("OCR_ENGINE", "glm")
OCR_TIMEOUT = float(os.getenv("OCR_TIMEOUT", "120"))
OCR_ENABLED = os.getenv("OCR_ENABLED", "true").lower() == "true"


async def extract_text(file_bytes: bytes, filename: str) -> str:
    if not OCR_ENABLED:
        raise RuntimeError("OCR service is disabled")

    async with httpx.AsyncClient(timeout=OCR_TIMEOUT) as client:
        response = await client.post(
            f"{OCR_URL}/extract",
            params={"engine": OCR_ENGINE},
            files={"file": (filename, file_bytes)},
        )
        response.raise_for_status()

    data = response.json()
    blocks = data.get("blocks", [])
    return "\n".join(b["content"] for b in blocks if b.get("content"))
