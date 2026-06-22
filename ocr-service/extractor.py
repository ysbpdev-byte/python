import threading
import os
from paddleocr import PaddleOCRVL

IDLE_TIMEOUT = int(os.getenv("MODEL_IDLE_TIMEOUT", "300"))  # detik, default 5 menit

_pipeline = None
_lock = threading.Lock()
_timer: threading.Timer | None = None


def _unload():
    global _pipeline
    with _lock:
        _pipeline = None


def _reset_timer():
    global _timer
    if _timer is not None:
        _timer.cancel()
    _timer = threading.Timer(IDLE_TIMEOUT, _unload)
    _timer.daemon = True
    _timer.start()


def _get_pipeline():
    global _pipeline
    with _lock:
        if _pipeline is None:
            _pipeline = PaddleOCRVL()
    _reset_timer()
    return _pipeline


def extract_text(file_path: str) -> list[dict]:
    pipeline = _get_pipeline()
    results = []

    for res in pipeline.predict(file_path):
        parsing = res.json.get("res", {}).get("parsing_res_list", [])
        for block in parsing:
            content = block.get("block_content", "").strip()
            if content:
                results.append({
                    "label": block.get("block_label"),
                    "content": content,
                    "bbox": block.get("block_bbox"),
                })

    return results
