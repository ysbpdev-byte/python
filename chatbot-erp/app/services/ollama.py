import os
import json
from pathlib import Path
import httpx
from dotenv import load_dotenv

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
                        "description": "Query SQL SELECT yang akan dijalankan terhadap database ERP"
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


def _build_system_prompt() -> str:
    return """Namamu adalah Hato, asisten AI dari ERP Hasta. Kamu membantu user menavigasi dan menggunakan sistem ERP Hasta.

Base URL ERP: http://hasta.crabdance.com:16132

Saat ini kamu memiliki akses ke modul HRD (Human Resource Development). Kedepannya kamu akan mendapatkan akses ke modul-modul lainnya.

## Aturan menjawab

Ada DUA jenis pertanyaan user — tangani dengan cara berbeda:

### 1. Pertanyaan navigasi menu (cara menggunakan ERP, di mana menu tertentu, dll)
- Jawab berdasarkan daftar menu HRD yang sudah diberikan
- Selalu sertakan URL lengkap (base URL + path)
- JANGAN sebut database, tabel, atau SQL sama sekali
- JANGAN panggil tool query_database

### 2. Pertanyaan data nyata (tampilkan data, berapa jumlah, siapa saja, dll)
- WAJIB panggil tool query_database
- JANGAN menolak dengan alasan tidak punya akses
- JANGAN mengarang data

### Umum
- Perkenalkan dirimu sebagai Hato jika user menyapa
- Jawab dalam Bahasa Indonesia yang ramah dan singkat
- Jika ditanya modul yang belum tersedia, sampaikan dengan sopan bahwa fitur belum tersedia"""


def _build_context_messages() -> list[dict]:
    context = _load_context()
    schema = _load_schema()

    messages = []
    messages.append({
        "role": "user",
        "content": f"Berikut adalah daftar menu HRD yang tersedia di ERP Hasta:\n\n{context}"
    })
    messages.append({
        "role": "assistant",
        "content": "Baik, saya sudah memahami menu-menu HRD yang tersedia."
    })

    if schema:
        messages.append({
            "role": "user",
            "content": f"Berikut adalah skema database ERP yang bisa kamu query menggunakan tool query_database:\n\n{schema}"
        })
        messages.append({
            "role": "assistant",
            "content": "Baik, saya sudah memahami skema database. Saya akan menggunakan tool query_database setiap kali user meminta data nyata dari database."
        })

    return messages


async def _call_ollama_once(messages: list[dict]) -> dict:
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,
        "think": False,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
        response.raise_for_status()
        return response.json()


async def chat_stream(messages: list[dict]):
    from app.services.database import run_select

    system_prompt = _build_system_prompt()
    context_messages = _build_context_messages()
    full_messages = [
        {"role": "system", "content": system_prompt},
        *context_messages,
        *messages,
    ]

    # Agentic loop: handle tool calls sampai tidak ada lagi
    tool_was_called = False
    while True:
        data = await _call_ollama_once(full_messages)
        msg = data.get("message", {})
        tool_calls = msg.get("tool_calls")
        print(f"[DEBUG] tool_calls: {tool_calls}", flush=True)
        print(f"[DEBUG] msg content: {msg.get('content', '')[:200]}", flush=True)

        if not tool_calls:
            if not tool_was_called:
                # Tidak ada tool call sama sekali — stream langsung jawaban non-streaming ini
                content = msg.get("content", "")
                if content:
                    yield content
                return
            # Setelah tool selesai — lanjut ke streaming final
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

    # Stream jawaban akhir setelah tool selesai
    payload = {
        "model": MODEL,
        "messages": full_messages,
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
