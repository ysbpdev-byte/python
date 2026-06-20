# OCR Service

REST API untuk extract teks dari gambar dan PDF menggunakan PaddleOCR-VL (layout analysis + VLM). Dioptimalkan untuk GPU NVIDIA Blackwell (RTX 5060 Ti, sm120).

## Requirement

- Docker + Docker Compose
- NVIDIA Container Toolkit
- GPU NVIDIA Blackwell (sm120) atau Ampere/Ada ke atas

## Menjalankan Service

```bash
cd ocr-service
sudo docker compose up -d
```

Service berjalan di port **2006**. Cek status:

```bash
sudo docker compose logs -f
```

Tunggu hingga muncul:
```
Uvicorn running on http://0.0.0.0:2006
```

## Endpoint

### `GET /health`

Cek apakah service berjalan.

**Response:**
```json
{"status": "ok"}
```

---

### `POST /extract`

Upload gambar atau PDF untuk di-extract teksnya.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` — file gambar atau PDF

**Format file yang didukung:**
`.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.tif`, `.webp`, `.pdf`

**Response:**
```json
{
  "filename": "invoice.jpg",
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
    },
    {
      "label": "paragraph_title",
      "content": "Total Pembayaran",
      "bbox": [27, 455, 341, 520]
    }
  ]
}
```

**Label yang mungkin muncul:**

| Label | Keterangan |
|-------|------------|
| `doc_title` | Judul dokumen |
| `paragraph_title` | Sub-judul / heading |
| `text` | Paragraf teks biasa |
| `table` | Konten tabel |
| `image` | Blok gambar (konten kosong) |
| `vision_footnote` | Caption gambar / footnote |

**Error:**
```json
{"detail": "File type '.xyz' not supported. Allowed: .jpg, .jpeg, ..."}
```

---

## Contoh Penggunaan

### curl

```bash
curl -X POST http://localhost:2006/extract \
  -F "file=@invoice.jpg"
```

### Python

```python
import requests

with open("invoice.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:2006/extract",
        files={"file": ("invoice.jpg", f, "image/jpeg")}
    )

data = response.json()
for block in data["blocks"]:
    print(f"[{block['label']}] {block['content']}")
```

### Swagger UI

Buka browser ke:
```
http://[IP-SERVER]:2006/docs
```

---

## Struktur Project

```
ocr-service/
├── main.py          # FastAPI app, routing, validasi file
├── extractor.py     # PaddleOCR-VL pipeline & parsing hasil
├── requirements.txt # Dependensi Python
├── compose.yaml     # Docker Compose config
└── README.md
```

## Manajemen Container

```bash
# Jalankan (background)
sudo docker compose up -d

# Lihat log realtime
sudo docker compose logs -f

# Stop
sudo docker compose down

# Restart
sudo docker compose restart
```
