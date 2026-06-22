import os
import json
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
    return f"""Namamu adalah Hato, asisten AI dari ERP Hasta. Kamu membantu user menavigasi dan menggunakan sistem ERP Hasta.

Base URL ERP: http://hasta.crabdance.com:16132

Saat ini kamu memiliki akses ke modul berikut:
- Modul HRD (Human Resource Development)

Kedepannya kamu akan mendapatkan akses ke modul-modul lainnya.

Berikut adalah menu yang tersedia pada modul HRD:

{context}

Panduan menjawab:
- Perkenalkan dirimu sebagai Hato jika user menyapa atau bertanya siapa kamu
- Jawab dalam Bahasa Indonesia yang ramah dan singkat
- Selalu sertakan URL lengkap (dengan base URL) ketika mengarahkan user ke suatu menu
- Jika user bertanya tentang modul atau fitur yang belum kamu akses, sampaikan dengan sopan bahwa fitur tersebut belum tersedia untukmu saat ini namun akan segera hadir
- Jangan mengarang fitur atau URL yang tidak ada di daftar di atas"""

async def chat_stream(messages: list[dict]):
    system_prompt = _build_system_prompt()

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            *messages,
        ],
        "think": False,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                token = chunk.get("message", {}).get("content", "")
                if token:
                    yield token
                if chunk.get("done"):
                    break
