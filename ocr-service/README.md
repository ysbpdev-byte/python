# OCR Service

REST API untuk ekstraksi teks dari gambar dan PDF, mendukung dua engine OCR yang bisa dipilih per request.

## Engine yang Tersedia

| Engine | Model | VRAM | Cocok untuk |
|---|---|---|---|
| `glm` | GLM-OCR via Ollama | ~4 GB | Default, ringan, akurasi bagus |
| `paddle` | PaddleOCR-VL | ~9-15 GB | Dokumen kompleks dengan tabel/chart |

## Cara Menjalankan

```bash
sudo docker compose up -d
```

Service berjalan di port `2006`. Kedua engine menggunakan **lazy loading** — model hanya dimuat ke VRAM saat ada request masuk, dan otomatis di-unload setelah idle `MODEL_IDLE_TIMEOUT` detik.

## Environment Variables

| Variable | Default | Keterangan |
|---|---|---|
| `DEFAULT_OCR_ENGINE` | `glm` | Engine default jika parameter `engine` tidak disertakan |
| `OLLAMA_HOST` | `http://172.17.0.1:11434` | URL Ollama server (`172.17.0.1` = host machine dari dalam container) |
| `OLLAMA_GLM_MODEL` | `glm-ocr` | Nama model GLM di Ollama |
| `MODEL_IDLE_TIMEOUT` | `300` | Detik sebelum model di-unload dari VRAM saat idle |

## API

### `POST /extract`

Ekstrak teks dari file gambar atau PDF.

**Query Parameters:**

| Parameter | Tipe | Default | Keterangan |
|---|---|---|---|
| `engine` | `glm` \| `paddle` | nilai `DEFAULT_OCR_ENGINE` | Engine OCR yang dipakai |

**Form Data:**

| Field | Tipe | Keterangan |
|---|---|---|
| `file` | file | File gambar atau PDF |

**Format yang didukung:** `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.tif`, `.webp`, `.pdf`

**Contoh Request:**

```bash
# Pakai engine default (glm)
curl -X POST "http://192.168.2.35:2006/extract" \
  -F "file=@document.jpg"

# Pilih engine secara eksplisit
curl -X POST "http://192.168.2.35:2006/extract?engine=glm" \
  -F "file=@document.jpg"

curl -X POST "http://192.168.2.35:2006/extract?engine=paddle" \
  -F "file=@document.jpg"
```

**Contoh Response (engine=glm):**

```json
{
  "filename": "delivery note.jpg",
  "engine": "glm",
  "blocks": [
    {
      "label": "text",
      "content": "PT. YANASURYA BHAKTIPERSADA\nJl. Pahlawan, Desa Banjarbendo...",
      "bbox": null
    }
  ]
}
```

**Contoh Response (engine=paddle):**

```json
{
  "filename": "invoice.jpg",
  "engine": "paddle",
  "blocks": [
    {
      "label": "doc_title",
      "content": "INVOICE",
      "bbox": [130, 35, 1384, 127]
    },
    {
      "label": "text",
      "content": "PT. Maju Jaya",
      "bbox": [8, 199, 361, 342]
    }
  ]
}
```

> **Catatan perbedaan output:**
> - `glm` → satu block berisi seluruh teks, `bbox` selalu `null`
> - `paddle` → beberapa block dengan label dan koordinat `bbox` per blok

**Label pada engine paddle:**

| Label | Keterangan |
|---|---|
| `doc_title` | Judul dokumen |
| `paragraph_title` | Sub-judul / heading |
| `text` | Paragraf teks biasa |
| `table` | Konten tabel |
| `image` | Blok gambar |
| `vision_footnote` | Caption / footnote |

---

### `GET /health`

Cek status service dan engine default yang aktif.

**Contoh Response:**

```json
{
  "status": "ok",
  "default_engine": "glm"
}
```

---

## Contoh Penggunaan

### Python

```python
import requests

with open("document.jpg", "rb") as f:
    response = requests.post(
        "http://192.168.2.35:2006/extract",
        files={"file": ("document.jpg", f, "image/jpeg")},
        params={"engine": "glm"},  # opsional
    )

data = response.json()
for block in data["blocks"]:
    print(f"[{block['label']}] {block['content']}")
```

---

## UI Testing

Swagger UI tersedia di:
```
http://192.168.2.35:2006/docs
```

---

## Arsitektur

```
Client
  │
  ▼
OCR Service (port 2006, Docker container)
  ├── engine=glm    ──► Ollama (port 11434, host machine) ──► GLM-OCR model
  └── engine=paddle ──► PaddleOCR-VL (dalam container)
```

## Kebutuhan VRAM (GPU: RTX 5060 Ti 16 GB)

| Kondisi | VRAM terpakai |
|---|---|
| Idle (tidak ada request) | ~160 MB |
| GLM-OCR loaded | ~4 GB |
| PaddleOCR-VL loaded | ~9-15 GB |
| GLM + Qwen3.5 (LLM lain) bersamaan | ~12 GB |

## Struktur Project

```
ocr-service/
├── main.py           # FastAPI app, routing, pemilihan engine
├── extractor.py      # Engine PaddleOCR-VL
├── extractor_glm.py  # Engine GLM-OCR via Ollama
├── requirements.txt  # Dependensi Python
├── compose.yaml      # Docker Compose config
└── README.md
```

## Manajemen Container

```bash
# Jalankan
sudo docker compose up -d

# Lihat log realtime
sudo docker compose logs -f

# Stop
sudo docker compose down

# Restart
sudo docker compose restart
```
