from typing import Optional

from pydantic import BaseModel, field_validator


# ======================================================
# Chat Request Model
# ======================================================

class ChatRequest(BaseModel):

    message: str

    session_id: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, value):

        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty.")

        if len(value) > 2000:
            raise ValueError("Message is too long.")

        return value


# ======================================================
# Chat Response Model
# ======================================================

class ChatResponse(BaseModel):

    session_id: str

    user_message: str

    ai_response: str

    model_used: str

    duration_ms: float

    eval_score: Optional[float] = None


# ======================================================
# Generate API Key Request
# ======================================================

class GenerateKeyRequest(BaseModel):

    user_name: str