import base64
import os
import threading
import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_GLM_MODEL", "glm-ocr")
IDLE_TIMEOUT = int(os.getenv("MODEL_IDLE_TIMEOUT", "300"))

_lock = threading.Lock()
_timer: threading.Timer | None = None


def _reset_timer():
    global _timer
    if _timer is not None:
        _timer.cancel()
    _timer = threading.Timer(IDLE_TIMEOUT, _unload_model)
    _timer.daemon = True
    _timer.start()


def _unload_model():
    requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={"model": OLLAMA_MODEL, "keep_alive": 0},
        timeout=10,
    )


def extract_text(file_path: str) -> list[dict]:
    with open(file_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    with _lock:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": "Extract all text from this document. Output only the extracted text, preserve the original layout as much as possible.",
                "images": [image_b64],
                "stream": False,
                "keep_alive": IDLE_TIMEOUT,
            },
            timeout=120,
        )
        response.raise_for_status()

    _reset_timer()

    text = response.json().get("response", "").strip()
    return [{"label": "text", "content": text, "bbox": None}]
