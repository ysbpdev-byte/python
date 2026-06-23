import os
import json
from pathlib import Path
import httpx
from dotenv import load_dotenv

from app.services.intent import (
    route_intent, NAVIGATION, DATA_QUERY, OTHER_MODULE, GREETING,
)
from app.services.menu import search_menu

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://192.168.2.35:11434")
MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5")

_context_cache: str | None = None
_schema_cache: str | None = None


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Jalankan SQL SELECT untuk mengambil data dari database ERP Hasta. Gunakan tool ini ketika user meminta data nyata seperti daftar karyawan, rekap absensi, status kontrak, dll.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "Query SQL SELECT yang akan dijalankan terhadap database ERP. PENTING: untuk pencarian nama atau teks, SELALU gunakan ILIKE dengan wildcard (%) bukan = atau LIKE. Contoh: WHERE name ILIKE '%matthew%' bukan WHERE name = 'matthew'. Ini karena data di database bisa huruf kapital semua atau campuran."
                    }
                },
                "required": ["sql"]
            }
        }
    }
]


def _load_context() -> str:
    global _context_cache
    if _context_cache is None:
        ctx_path = Path(__file__).parent.parent / "context" / "hrd.md"
        _context_cache = ctx_path.read_text(encoding="utf-8")
    return _context_cache


def _load_schema() -> str:
    global _schema_cache
    if _schema_cache is None:
        schema_path = Path(__file__).parent.parent / "context" / "db_schema.md"
        if schema_path.exists():
            _schema_cache = schema_path.read_text(encoding="utf-8")
        else:
            _schema_cache = ""
    return _schema_cache


# ---------------------------------------------------------------------------
# Penyusunan prompt per-intent
# ---------------------------------------------------------------------------

def _base_persona() -> str:
    return """Namamu adalah Hato, asisten AI dari ERP Hasta. Kamu membantu user menavigasi dan menggunakan sistem ERP Hasta.

Base URL ERP: http://hasta.crabdance.com:16132
Saat ini kamu hanya memiliki akses ke modul HRD (Human Resource Development).
Jawab dalam Bahasa Indonesia yang ramah dan singkat."""


def _system_for(intent: str, retrieved_menu: str | None) -> str:
    persona = _base_persona()

    if intent == NAVIGATION:
        return f"""{persona}

User sedang menanyakan navigasi/menu HRD. Di bawah ini adalah DAFTAR MENU yang relevan dengan pertanyaannya:

==============================
{retrieved_menu or "(tidak ada menu yang cocok ditemukan)"}
==============================

ATURAN:
- Jawab HANYA berdasarkan daftar menu di atas.
- SALIN URL secara verbatim (path persis seperti di daftar). Tampilkan URL lengkap = Base URL + path.
- DILARANG mengarang, menebak, atau mengubah URL. Jika menu yang diminta tidak ada di daftar di atas, katakan: "Maaf, menu tersebut tidak saya temukan di modul HRD."
- JANGAN sebut kata "database", "tabel", "SQL", atau "query"."""

    if intent == DATA_QUERY:
        return f"""{persona}

User meminta DATA NYATA dari sistem. Kamu memiliki tool `query_database` untuk mengambil data.

ATURAN:
- WAJIB panggil tool `query_database` untuk mengambil data. JANGAN mengarang data. JANGAN menolak dengan alasan tidak punya akses.
- Setelah hasil kembali, sajikan dengan ramah. JANGAN sebut kata "database", "tabel", "SQL", atau "query" kepada user.

Aturan penulisan SQL:
- Pencarian nama/teks SELALU gunakan ILIKE dengan wildcard: WHERE name ILIKE '%keyword%'
- JANGAN gunakan = untuk mencari nama/teks, karena data di database bisa huruf kapital semua.
- Contoh BENAR: WHERE e.name ILIKE '%matthew%'
- Contoh SALAH: WHERE e.name = 'Matthew Kevin'"""

    if intent == OTHER_MODULE:
        return f"""{persona}

User menanyakan modul di luar HRD. Jawab dengan sopan: "Maaf, saat ini saya hanya bisa membantu untuk modul HRD. Modul tersebut belum tersedia." Jangan mengarang informasi."""

    # GREETING / default
    return f"""{persona}

Perkenalkan dirimu sebagai Hato dan jelaskan bahwa kamu bisa membantu menavigasi menu HRD serta menampilkan data dari sistem ERP Hasta. Singkat dan ramah."""


def _data_context_pair() -> list[dict]:
    """Skema database sebagai pasangan user/assistant. Hanya dipakai untuk DATA_QUERY."""
    schema = _load_schema()
    if not schema:
        return []
    return [
        {
            "role": "user",
            "content": f"Berikut adalah skema tabel yang bisa kamu gunakan saat memanggil tool query_database:\n\n{schema}",
        },
        {
            "role": "assistant",
            "content": "Baik, saya sudah memahami skema tabelnya. Saya akan memanggil tool query_database setiap kali user meminta data nyata dari sistem.",
        },
    ]


def _sanitize_history(messages: list[dict], keep_turns: int = 4) -> list[dict]:
    """Higiene history: buang artefak tool & pesan kosong, sisakan beberapa turn terakhir.

    Hanya menyimpan role user/assistant dengan content non-kosong, lalu memotong
    ke `keep_turns * 2` pesan terakhir. Mencegah priming berlebih yang membuat
    model terpaku memanggil tool.
    """
    clean = [
        {"role": m["role"], "content": m["content"]}
        for m in messages
        if m.get("role") in ("user", "assistant") and m.get("content", "").strip()
    ]
    if keep_turns > 0:
        clean = clean[-(keep_turns * 2):]
    return clean


# ---------------------------------------------------------------------------
# Plumbing Ollama
# ---------------------------------------------------------------------------

async def _call_ollama_once(messages: list[dict], tools: list | None) -> dict:
    payload = {
        "model": MODEL,
        "messages": messages,
        "think": False,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
        response.raise_for_status()
        return response.json()


async def _stream_chat(full_messages: list[dict], tools: list | None = None):
    """Streaming jawaban. Bila tools=None, model tidak dapat memanggil tool sama sekali."""
    payload = {
        "model": MODEL,
        "messages": full_messages,
        "think": False,
        "stream": True,
    }
    if tools:
        payload["tools"] = tools
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


async def _agentic_then_stream(full_messages: list[dict]):
    """Loop tool query_database sampai selesai, lalu stream jawaban akhir."""
    from app.services.database import run_select

    tool_was_called = False
    while True:
        data = await _call_ollama_once(full_messages, tools=TOOLS)
        msg = data.get("message", {})
        tool_calls = msg.get("tool_calls")
        print(f"[DEBUG] tool_calls: {tool_calls}", flush=True)
        print(f"[DEBUG] msg content: {msg.get('content', '')[:200]}", flush=True)

        if not tool_calls:
            if not tool_was_called:
                content = msg.get("content", "")
                if content:
                    yield content
                return
            break

        tool_was_called = True
        full_messages.append(msg)

        for tc in tool_calls:
            fn = tc.get("function", {})
            tool_name = fn.get("name")
            args = fn.get("arguments", {})

            if tool_name == "query_database":
                try:
                    rows = await run_select(args.get("sql", ""))
                    result = json.dumps(rows, ensure_ascii=False, default=str)
                except Exception as e:
                    result = json.dumps({"error": str(e)}, ensure_ascii=False)
            else:
                result = json.dumps({"error": f"Tool '{tool_name}' tidak dikenal"})

            full_messages.append({
                "role": "tool",
                "content": result,
                "tool_name": tool_name,
            })

    async for token in _stream_chat(full_messages, tools=None):
        yield token


# ---------------------------------------------------------------------------
# Handler per-intent
# ---------------------------------------------------------------------------

async def _handle_navigation(latest: str, history: list[dict]):
    menu = search_menu(latest)
    full = [
        {"role": "system", "content": _system_for(NAVIGATION, menu)},
        *history,
        {"role": "user", "content": latest},
    ]
    async for token in _stream_chat(full, tools=None):
        yield token


async def _handle_data(latest: str, history: list[dict]):
    full = [
        {"role": "system", "content": _system_for(DATA_QUERY, None)},
        *_data_context_pair(),
        *history,
        {"role": "user", "content": latest},
    ]
    async for token in _agentic_then_stream(full):
        yield token


async def _handle_simple(intent: str, latest: str, history: list[dict]):
    full = [
        {"role": "system", "content": _system_for(intent, None)},
        *history,
        {"role": "user", "content": latest},
    ]
    async for token in _stream_chat(full, tools=None):
        yield token


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def chat_stream(messages: list[dict]):
    latest = messages[-1]["content"]
    intent = await route_intent(latest)
    print(f"[DEBUG] intent: {intent}", flush=True)
    history = _sanitize_history(messages[:-1])

    if intent == DATA_QUERY:
        async for token in _handle_data(latest, history):
            yield token
    elif intent == NAVIGATION:
        async for token in _handle_navigation(latest, history):
            yield token
    else:  # OTHER_MODULE / GREETING
        async for token in _handle_simple(intent, latest, history):
            yield token
