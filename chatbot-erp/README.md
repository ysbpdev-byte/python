# Hato — Chatbot Asisten ERP Hasta

Hato adalah chatbot AI yang membantu pengguna sistem ERP Hasta untuk:
- Menavigasi menu dan fitur ERP
- Mengambil data langsung dari database via SQL query (SELECT only)

Saat ini Hato memiliki akses ke **Modul HRD**. Modul lainnya akan ditambahkan secara bertahap.

---

## Arsitektur

```
ERP Laravel ──POST /api/chat──► Chatbot Service (FastAPI) ──► Ollama (Qwen3.5)
                                        │
                                        ▼ (jika butuh data)
                                  PostgreSQL ERP DB
```

**Tech Stack:**
- Python 3.12 + FastAPI
- Ollama (self-hosted LLM — Qwen3.5)
- asyncpg (koneksi PostgreSQL async)
- Docker

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
    │   ├── ollama.py            # Ollama client + tool calling + agentic loop
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

**Catatan:** `messages` adalah array penuh percakapan. Klien (ERP) bertanggung jawab menyimpan dan mengirimkan history percakapan di setiap request.

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

### Navigasi Menu
Jika user bertanya tentang menu atau fitur ERP, Hato langsung menjawab berdasarkan konteks di `app/context/hrd.md` tanpa memanggil database.

```
User: "Saya mau ajukan cuti"
Hato: "Silakan ke menu Buat Pengajuan Cuti di http://hasta.crabdance.com:16132/hr/leaves/create"
```

### Query Database (Agentic Loop)
Jika user meminta data nyata, Hato menggunakan tool `query_database`:

```
User: "Tampilkan 5 karyawan terbaru"
  → Hato generate SQL SELECT
  → SQL dieksekusi ke PostgreSQL (SELECT only, maks 100 baris)
  → Hasil dikembalikan ke Hato
  → Hato format hasil menjadi jawaban natural language → stream ke user
```

**Keamanan SQL:**
- Hanya `SELECT` yang diizinkan
- `LIMIT 100` otomatis ditambahkan jika tidak ada
- Gunakan user PostgreSQL dengan privilege `SELECT` saja

---

## Menambah Konteks Modul Baru

1. Buat file markdown di `app/context/` (contoh: `finance.md`)
2. Update system prompt di `app/services/ollama.py` untuk load file baru
3. Restart service: `docker compose restart`

Tidak perlu rebuild image jika hanya mengubah file context (karena di-mount sebagai volume).

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
