import os
from pathlib import Path
import httpx
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://192.168.2.35:11434")
MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5")

_context_cache: str | None = None

def _load_context() -> str:
    global _context_cache
    if _context_cache is None:
        ctx_path = Path(__file__).parent.parent / "context" / "hrd.md"
        _context_cache = ctx_path.read_text(encoding="utf-8")
    return _context_cache

def _build_system_prompt() -> str:
    context = _load_context()
    return f"""Kamu adalah asisten ERP Hasta yang membantu user menemukan menu yang tepat di sistem ERP.

Base URL ERP: http://hasta.crabdance.com:16132

Berikut adalah daftar lengkap modul dan menu yang tersedia di modul HRD:

{context}

Panduan menjawab:
- Jawab dalam Bahasa Indonesia yang ramah dan singkat
- Selalu sertakan URL lengkap (dengan base URL) ketika mengarahkan user ke suatu menu
- Jika user bertanya sesuatu yang tidak ada di modul HRD, sampaikan dengan sopan bahwa kamu hanya bisa membantu navigasi modul HRD untuk saat ini
- Jangan mengarang fitur atau URL yang tidak ada di daftar di atas"""

async def chat(messages: list[dict]) -> str:
    system_prompt = _build_system_prompt()

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            *messages,
        ],
        "think": False,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]
