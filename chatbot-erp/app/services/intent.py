"""Klasifikasi intent pesan user (keyword-first, fallback LLM untuk ambigu).

Routing menentukan handler mana yang dipakai di ollama.py dan — yang terpenting —
apakah tool query_database dilampirkan. Kasus umum diselesaikan oleh aturan
keyword (0 latensi tambahan); hanya kasus ambigu yang memicu panggilan LLM kecil.
"""
import os
import re
import httpx
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://192.168.2.35:11434")
MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5")

NAVIGATION = "NAVIGATION"
DATA_QUERY = "DATA_QUERY"
OTHER_MODULE = "OTHER_MODULE"
GREETING = "GREETING"
AMBIGUOUS = "AMBIGUOUS"  # sentinel internal -> picu fallback LLM

_VALID_LABELS = {NAVIGATION, DATA_QUERY, OTHER_MODULE, GREETING}

# Modul di luar HRD. Dicek paling awal supaya "lihat data penjualan" tidak salah
# diklasifikasi sebagai DATA_QUERY (yang akan mencoba query DB HRD).
_OTHER_MODULE_KW = [
    "keuangan", "akuntansi", "finance", "inventory", "inventaris gudang",
    "pembelian", "penjualan", "produksi", "gudang", "stok", "purchasing",
    "sales", "akunting", "jurnal", "neraca", "laba rugi",
]

# Frasa yang menandakan user minta DATA NYATA dari sistem.
_DATA_KW = [
    "berapa", "jumlah", "total", "tampilkan data", "tampilkan daftar",
    "siapa saja", "siapa yang", "rekap", "statistik", "rata-rata", "rata rata",
    "daftar nama", "list nama", "ada berapa", "hitung", "jumlahnya",
    "cek status", "cek kontrak", "cek absensi", "cek data",
]

# Frasa yang menandakan user butuh NAVIGASI / cara pakai menu.
_NAV_KW = [
    "di mana", "dimana", "letak", "menu", "cara", "bagaimana", "gimana",
    "buka", "akses", "halaman", "link", "url", "navigasi", "navigasikan",
    "saya mau", "saya ingin", "mau ajukan", "mau buat", "mau tambah",
    "mau lihat menu", "ke halaman", "fitur",
]

_GREETING_KW = [
    "halo", "hai", "hi", "hello", "pagi", "siang", "sore", "malam",
    "terima kasih", "makasih", "thanks", "siapa kamu", "kamu siapa",
    "kamu bisa apa", "bisa apa", "apa itu hato", "perkenalkan",
]


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(kw in text for kw in keywords)


def classify_intent(latest_user_text: str) -> str:
    """Klasifikasi deterministik berbasis keyword. Urutan prioritas penting.

    Mengembalikan salah satu label valid, atau AMBIGUOUS bila tak ada aturan
    yang cukup yakin.
    """
    text = latest_user_text.lower().strip()
    if not text:
        return GREETING

    # 1. Modul lain — paling spesifik, cek dulu.
    if _contains_any(text, _OTHER_MODULE_KW):
        return OTHER_MODULE

    has_data = _contains_any(text, _DATA_KW)
    has_nav = _contains_any(text, _NAV_KW)

    # 2/3. Data vs navigasi. Bila keduanya muncul ("di mana menu cuti dan berapa
    # yang cuti"), prioritaskan DATA_QUERY karena tool memang yang dibutuhkan.
    if has_data and not has_nav:
        return DATA_QUERY
    if has_nav and not has_data:
        return NAVIGATION
    if has_data and has_nav:
        return DATA_QUERY

    # 4. Sapaan singkat.
    if _contains_any(text, _GREETING_KW):
        return GREETING

    # 5. Tidak yakin -> serahkan ke LLM.
    return AMBIGUOUS


async def classify_intent_llm(latest_user_text: str) -> str:
    """Fallback klasifikasi via LLM kecil. Tanpa tools, tanpa menu/schema, satu kata.

    Hanya dipanggil saat classify_intent mengembalikan AMBIGUOUS.
    """
    prompt = (
        "Klasifikasikan pesan user ke SATU label saja. Jawab HANYA dengan satu kata "
        "label, tanpa penjelasan.\n\n"
        "Label yang tersedia:\n"
        "- NAVIGATION : user menanyakan letak/cara akses menu atau cara melakukan sesuatu di aplikasi HRD\n"
        "- DATA_QUERY : user meminta data nyata (jumlah, daftar, rekap, status seseorang)\n"
        "- OTHER_MODULE : user menanyakan modul selain HRD (keuangan, penjualan, gudang, dll)\n"
        "- GREETING : sapaan atau pertanyaan umum tentang chatbot\n\n"
        f"Pesan user: \"{latest_user_text}\"\n\n"
        "Label:"
    )
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "think": False,
        "stream": False,
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "")
    except Exception:
        # Bila LLM gagal, default ke NAVIGATION (lebih aman: tanpa tool, tak query DB).
        return NAVIGATION

    upper = content.upper()
    for label in _VALID_LABELS:
        if label in upper:
            return label
    return NAVIGATION


async def route_intent(latest_user_text: str) -> str:
    """Entry-point routing: keyword dulu, fallback LLM hanya bila ambigu."""
    label = classify_intent(latest_user_text)
    if label == AMBIGUOUS:
        label = await classify_intent_llm(latest_user_text)
    return label
