from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import ollama

router = APIRouter()

class Message(BaseModel):
    role: str   # "user" atau "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    session_id: str | None = None   # opsional, untuk tracking dari ERP

class ChatResponse(BaseModel):
    success: bool
    reply: str
    session_id: str | None = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages tidak boleh kosong")

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    try:
        reply = await ollama.chat(messages)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gagal menghubungi Ollama: {str(e)}")

    return ChatResponse(success=True, reply=reply, session_id=request.session_id)
