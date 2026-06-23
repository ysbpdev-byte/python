"""Retrieval menu navigasi dari hrd.md.

Tujuannya men-grounding jawaban navigasi: model hanya menerima section menu
yang relevan (markdown verbatim, URL persis dari file) alih-alih seluruh daftar
~3400 token. Ini menekan halusinasi URL sekaligus context length.
"""
import re
from pathlib import Path
from dataclasses import dataclass, field

_CTX_PATH = Path(__file__).parent.parent / "context" / "hrd.md"

# Tabel "Ringkasan Pertanyaan Umum" dipakai sebagai fallback aman bila tidak ada
# section yang cocok. Judulnya di hrd.md diawali kata "Ringkasan".
_SUMMARY_TITLE_HINT = "ringkasan"

# Sinonim Indonesia -> kata yang muncul di Label/URL section. Membantu query user
# ("cuti") cocok dengan section yang labelnya "Leave"/URL "/hr/leaves".
_SYNONYMS = {
    "cuti": ["leaves", "leave", "izin"],
    "izin": ["leaves", "leave"],
    "karyawan": ["employees", "employee", "pegawai"],
    "pegawai": ["employees", "employee"],
    "kontrak": ["contracts", "contract", "pkwt", "pkwtt"],
    "absensi": ["attendance", "kehadiran", "absen"],
    "kehadiran": ["attendance"],
    "pelatihan": ["trainings", "training", "diklat"],
    "rekrutmen": ["recruitment", "screening", "kandidat", "candidates", "lowongan", "pelamar"],
    "lowongan": ["recruitment", "requests"],
    "kandidat": ["screening", "candidates"],
    "aset": ["assets", "asset", "inventaris"],
    "kendaraan": ["vehicles", "vehicle", "armada", "mobil"],
    "mutasi": ["mutation", "pindah", "rotasi", "promosi"],
    "tamu": ["appointments", "kunjungan", "guest"],
    "kunjungan": ["appointments"],
    "kecelakaan": ["work-accident", "accident", "insiden", "k3"],
    "jadwal": ["work_schedules", "schedule", "shift"],
    "shift": ["work_schedules", "schedule"],
    "tugas": ["assignments", "assignment", "penugasan"],
    "penugasan": ["assignments"],
    "job": ["job-desk", "jobdesk", "deskripsi"],
    "desk": ["job-desk"],
    "jobdesk": ["job-desk"],
    "maintenance": ["maintenance-tickets", "perbaikan", "tiket", "kerusakan"],
    "perbaikan": ["maintenance-tickets"],
    "aktivitas": ["cms", "activities"],
    "dashboard": ["dashboard"],
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_HEADER_RE = re.compile(r"^#{2,3}\s+(.*)$")
# Segmen path dari URL dalam backtick, mis. `/hr/leaves/create` -> leaves, create
_URL_SEG_RE = re.compile(r"/hr/([a-z0-9_\-/]+)", re.IGNORECASE)


@dataclass
class Section:
    title: str
    body: str
    keywords: set[str] = field(default_factory=set)
    is_summary: bool = False


_sections_cache: list[Section] | None = None


def _tokenize(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def _section_keywords(title: str, body: str) -> set[str]:
    kw: set[str] = set()
    kw |= _tokenize(title)
    # Setiap segmen path URL pada section ini (leaves, create, employees, ...).
    for path in _URL_SEG_RE.findall(body):
        for seg in path.split("/"):
            seg = seg.strip()
            # Lewati placeholder seperti {id}, {uuid}.
            if seg and not seg.startswith("{"):
                kw |= _tokenize(seg)
    # Kolom Label dari tiap baris tabel: ambil cell pertama.
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("|") and "|" in line[1:]:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells and not set(cells[0]) <= {"-", " "}:  # bukan baris separator
                kw |= _tokenize(cells[0])
    return kw


def _load_sections() -> list[Section]:
    global _sections_cache
    if _sections_cache is not None:
        return _sections_cache

    text = _CTX_PATH.read_text(encoding="utf-8")
    sections: list[Section] = []
    cur_title: str | None = None
    cur_lines: list[str] = []

    def flush():
        if cur_title is None:
            return
        body = "\n".join(cur_lines).strip()
        if not body and not cur_title:
            return
        is_summary = _SUMMARY_TITLE_HINT in cur_title.lower()
        sections.append(Section(
            title=cur_title,
            body=body,
            keywords=_section_keywords(cur_title, body),
            is_summary=is_summary,
        ))

    for line in text.splitlines():
        m = _HEADER_RE.match(line)
        if m:
            flush()
            cur_title = m.group(1).strip()
            cur_lines = []
        elif cur_title is not None:
            cur_lines.append(line)
    flush()

    _sections_cache = sections
    return sections


def _expand_query_tokens(query: str) -> set[str]:
    tokens = _tokenize(query)
    expanded = set(tokens)
    for tok in tokens:
        if tok in _SYNONYMS:
            expanded.update(_SYNONYMS[tok])
    return expanded


def search_menu(query: str, max_sections: int = 2) -> str:
    """Kembalikan markdown verbatim dari section menu yang paling relevan.

    Skor = jumlah token query (sudah diperluas sinonim) yang cocok dengan
    keyword section. Section ringkasan tidak ikut diskor; ia hanya dipakai
    sebagai fallback saat tidak ada section yang cocok.
    """
    sections = _load_sections()
    q_tokens = _expand_query_tokens(query)

    scored: list[tuple[int, Section]] = []
    summary: Section | None = None
    for sec in sections:
        if sec.is_summary:
            summary = sec
            continue
        score = len(q_tokens & sec.keywords)
        if score > 0:
            scored.append((score, sec))

    if not scored:
        if summary is not None:
            return f"## {summary.title}\n\n{summary.body}"
        return ""

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:max_sections]
    return "\n\n".join(f"## {sec.title}\n\n{sec.body}" for _, sec in top)
