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
            async for token in ollama.chat_stream(messages):
                yield token
        except Exception as e:
            yield f"\n[Error: {str(e)}]"

    return StreamingResponse(generate(), media_type="text/plain")
