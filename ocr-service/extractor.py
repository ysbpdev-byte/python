from paddleocr import PaddleOCRVL

_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = PaddleOCRVL()
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
