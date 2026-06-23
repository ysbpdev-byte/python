# Hato — Chatbot Asisten ERP Hasta

Hato adalah chatbot AI yang membantu pengguna sistem ERP Hasta untuk:
- Menavigasi menu dan fitur ERP
- Mengambil data langsung dari database via SQL query (SELECT only)

Saat ini Hato memiliki akses ke **Modul HRD**. Modul lainnya akan ditambahkan secara bertahap.

---

## Arsitektur

```
ERP Laravel ──POST /api/chat──► Chatbot Service (FastAPI)
                                        │
                                        ▼
                              Intent Router (keyword + LLM fallback)
                                        │
                ┌───────────────────────┼───────────────────────┐
                ▼                       ▼                       ▼
         NAVIGATION              DATA_QUERY            OTHER_MODULE / GREETING
     (retrieval menu,        (agentic loop +              (jawaban langsung,
      TANPA tool)             tool query_database)          TANPA tool)
                │                       │
                ▼                       ▼
       hrd.md (verbatim)         Ollama (Qwen) ──► PostgreSQL ERP DB
```

**Tech Stack:**
- Python 3.12 + FastAPI
- Ollama (self-hosted LLM — Qwen)
- asyncpg (koneksi PostgreSQL async)
- Docker

**Prinsip desain:** setiap pesan user dirutekan ke salah satu *intent* lebih dulu.
Tool `query_database` **hanya** dilampirkan saat intent `DATA_QUERY`. Untuk
navigasi, model tidak diberi tool sama sekali dan hanya menerima potongan menu
yang relevan dari `hrd.md` (verbatim) — sehingga URL tidak mungkin dikarang dan
model tidak "terpaku" memanggil database pada pertanyaan yang bukan soal data.

---

## Struktur Folder

```
chatbot-erp/
├── main.py                      # Entry point FastAPI + CORS
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                         # Konfigurasi (tidak di-commit)
├── .env.example                 # Template konfigurasi
├── static/
│   └── index.html               # Chat UI untuk testing
└── app/
    ├── routes/
    │   └── chat.py              # POST /api/chat
    ├── services/
    │   ├── intent.py            # Klasifikasi intent (keyword + fallback LLM)
    │   ├── menu.py              # Retrieval section menu dari hrd.md (verbatim)
    │   ├── ollama.py            # Dispatcher per-intent + tool calling + agentic loop
    │   └── database.py          # SQL executor (SELECT only, max 100 rows)
    └── context/
        ├── hrd.md               # Konteks navigasi menu HRD
        └── db_schema.md         # Skema tabel DB yang boleh di-query
```

---

## Konfigurasi

Salin `.env.example` ke `.env` dan sesuaikan:

```env
OLLAMA_URL=http://<ip-server>:11434
OLLAMA_MODEL=qwen3.5

# Domain ERP yang boleh akses (pisah koma, atau * untuk semua)
ALLOWED_ORIGINS=http://hasta.crabdance.com:16132

# Koneksi PostgreSQL ERP (READ-ONLY user direkomendasikan)
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

---

## Menjalankan

### Dengan Docker (direkomendasikan)

```bash
cp .env.example .env
# Edit .env sesuai environment

docker compose up -d --build
```

### Tanpa Docker

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Endpoint API

### `POST /api/chat`

Mengirim pesan ke Hato. Response berupa **text stream** (token per token).

**Request:**
```json
{
  "session_id": "user_123",
  "messages": [
    { "role": "user", "content": "tampilkan karyawan yang kontraknya habis bulan ini" }
  ]
}
```

**Response:** `text/plain` stream

```
Berikut karyawan yang kontraknya akan habis bulan ini:
1. Budi Santoso — berakhir 30 Juni 2026
2. Siti Rahma — berakhir 28 Juni 2026
...
```

**Field:**
- `messages` (wajib): array penuh percakapan. Klien (ERP) bertanggung jawab
  menyimpan dan mengirimkan history di setiap request. Pesan dengan `content`
  kosong diabaikan; jika semua pesan kosong, response `400`.
- `session_id` (opsional): hanya dipakai untuk penelusuran log saat ini
  (tidak ada penyimpanan history di sisi server).

---

### `GET /health`

Cek status service.

**Response:**
```json
{ "status": "ok" }
```

---

### `GET /`

Chat UI untuk testing langsung via browser.

---

## Cara Kerja Hato

Setiap pesan user melewati **3 tahap**: routing intent → muat konteks yang
relevan → generate jawaban. Kuncinya: konteks dan tool yang dimuat berbeda-beda
tergantung intent, sehingga model tidak kebanjiran konteks dan tidak salah pilih
antara "cari menu" vs "cari data".

### Tahap 1 — Routing Intent (`app/services/intent.py`)

`route_intent()` mengklasifikasi **pesan terakhir** user ke salah satu label:

| Label | Contoh pesan | Penanganan |
|---|---|---|
| `NAVIGATION` | "di mana menu cuti", "cara tambah karyawan" | Retrieval menu, **tanpa** tool |
| `DATA_QUERY` | "berapa karyawan aktif", "siapa yang cuti hari ini" | Agentic loop + tool `query_database` |
| `OTHER_MODULE` | "lihat data penjualan", "menu keuangan" | Jawaban penolakan sopan |
| `GREETING` | "halo", "kamu bisa apa" | Perkenalan singkat |

Klasifikasi memakai **keyword** lebih dulu (instan, tanpa panggilan model). Hanya
jika pesan ambigu, dilakukan **satu panggilan LLM kecil** sebagai fallback.
Label routing dapat dilihat di log: `[DEBUG] intent: NAVIGATION`.

### Tahap 2 — Navigasi Menu (`app/services/menu.py`)

Untuk intent `NAVIGATION`, `search_menu()` mengambil **hanya section menu yang
relevan** dari `app/context/hrd.md` (dicocokkan via keyword + sinonim), lalu
menyisipkannya **verbatim** ke prompt. Model diinstruksikan menyalin URL persis
apa adanya dan menolak jika menu tidak ada di daftar.

```
User: "Saya mau ajukan cuti"
  → intent: NAVIGATION
  → search_menu mengambil section "Cuti & Izin" dari hrd.md
  → Hato: "Silakan ke menu Buat Pengajuan Cuti di
            http://hasta.crabdance.com:16132/hr/leaves/create"
```

Pada tahap ini tool `query_database` **tidak dilampirkan sama sekali**, sehingga
model secara struktural tidak bisa (dan tidak tergoda) memanggil database.

### Tahap 3 — Query Database / Agentic Loop (`app/services/ollama.py`)

Untuk intent `DATA_QUERY`, skema tabel (`db_schema.md`) dimuat dan tool
`query_database` dilampirkan:

```
User: "Tampilkan 5 karyawan terbaru"
  → intent: DATA_QUERY
  → Hato generate SQL SELECT
  → SQL dieksekusi ke PostgreSQL (SELECT only, maks 100 baris)
  → Hasil dikembalikan ke Hato
  → Hato format hasil menjadi jawaban natural language → stream ke user
```

**Keamanan SQL:**
- Hanya `SELECT` yang diizinkan
- `LIMIT 100` otomatis ditambahkan jika tidak ada
- Gunakan user PostgreSQL dengan privilege `SELECT` saja

### Manajemen History

History percakapan dikirim penuh oleh klien di setiap request, lalu
**dibersihkan di server** (`_sanitize_history`): artefak tool dibuang dan hanya
±4 turn terakhir yang dipertahankan. Ini mencegah jawaban data lama "mem-prime"
model agar terus memanggil tool pada turn navigasi berikutnya.

---

## Menambah Konteks Modul Baru

Arsitektur saat ini dirancang untuk modul HRD. Untuk menambah modul baru:

1. **Buat file context** markdown di `app/context/` (contoh: `finance.md`),
   ikuti struktur `hrd.md` (header `##`/`###` per section + tabel
   `| Label | URL | Kegunaan |`).
2. **Daftarkan label intent baru** di `app/services/intent.py`:
   - Pindahkan keyword modul tersebut dari `_OTHER_MODULE_KW` (yang saat ini
     menolaknya) ke daftar keyword intent navigasi/data yang sesuai.
3. **Tambah retrieval** untuk file context baru (mengikuti pola `app/services/menu.py`),
   dan arahkan handler di `app/services/ollama.py` (`chat_stream` dispatcher) ke
   konteks tersebut.
4. **Restart service:** `docker compose restart`.

> Mengubah **isi** file context (`hrd.md`, `db_schema.md`) saja tidak perlu
> rebuild image — folder `app/context` di-mount sebagai volume, cukup
> `docker compose restart`. Namun menambah **kode** (modul/handler baru) tetap
> perlu `docker compose up -d --build`.

---

## Update & Deployment

```bash
# Pull perubahan terbaru
git pull

# Rebuild dan restart
docker compose up -d --build

# Cek log
docker compose logs -f

# Cek status
docker compose ps
curl http://localhost:2206/health
```

---

## Integrasi dengan Laravel

```php
// Simpan history di session
$history = session('hato_history_' . $sessionId, []);
$history[] = ['role' => 'user', 'content' => $userMessage];

$response = Http::timeout(120)->post('http://localhost:2206/api/chat', [
    'session_id' => $sessionId,
    'messages'   => $history,
]);

$reply = $response->body(); // plain text stream
$history[] = ['role' => 'assistant', 'content' => $reply];
session(['hato_history_' . $sessionId => $history]);
```
