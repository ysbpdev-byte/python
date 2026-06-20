import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Chatbot ERP HRD")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(chat_router, prefix="/api")

@app.get("/")
def index():
    return FileResponse("static/index.html")

@app.get("/health")
def health():
    return {"status": "ok"}
