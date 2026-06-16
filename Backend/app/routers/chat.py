from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from app.ai.rag_service import ask_chatbot
from app.core.rate_limit import limiter
from app.core.security import require_premium
from app.models.user import User

router = APIRouter(prefix="/chat", tags=["Chatbot"])


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    # Prior turns for conversation memory (most recent last). Capped server-side.
    history: Optional[List[ChatMessage]] = Field(default=None, max_length=50)


class ChatResponse(BaseModel):
    reply: str


@router.post("/ask", response_model=ChatResponse)
@limiter.limit("15/minute")
def chat(
    request: Request,
    req: ChatRequest,
    current_user: User = Depends(require_premium),
):
    history = [m.model_dump() for m in req.history] if req.history else None
    answer = ask_chatbot(req.message, history=history)
    return {"reply": answer}