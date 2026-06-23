from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services import ollama

router = APIRouter()

class Message(BaseModel):
    role: str   # "user" atau "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    session_id: str | None = None

@router.post("/chat")
async def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages tidak boleh kosong")

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    async def generate():
        try:
            print(f"[DEBUG] chat_stream dipanggil dengan {len(messages)} pesan, session_id={request.session_id}", flush=True)
            async for token in ollama.chat_stream(messages, session_id=request.session_id):
                yield token
        except Exception as e:
            print(f"[DEBUG] Error: {e}", flush=True)
            yield f"\n[Error: {str(e)}]"

    return StreamingResponse(generate(), media_type="text/plain")
