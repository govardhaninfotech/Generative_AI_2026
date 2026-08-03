from fastapi import (
    APIRouter,
    Depends
)

from auth import verify_api_key

from models import ChatRequest

from services.stream_service import (
    process_stream_chat
)

router = APIRouter(
    prefix="",
    tags=["Streaming"]
)


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user: str = Depends(verify_api_key)
):
    return await process_stream_chat(
        request,
        user
    )