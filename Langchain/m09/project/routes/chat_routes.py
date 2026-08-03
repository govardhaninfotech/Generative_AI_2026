from fastapi import APIRouter, Depends
from auth import verify_api_key
from models import ChatRequest, ChatResponse
from services.chat_service import process_chat

router = APIRouter(prefix="", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    user = "developer"
    return process_chat(request, user)
