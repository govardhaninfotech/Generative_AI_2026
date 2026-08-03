import secrets
import sqlite3

from fastapi import (
    APIRouter,
    Header,
    HTTPException
)

from auth import hash_key

from database import get_connection

from config import ADMIN_KEY

from middleware import logger

from models import GenerateKeyRequest


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/generate-key")
def generate_key(
    request: GenerateKeyRequest,
    x_api_key: str = Header(...)
):

    if x_api_key != ADMIN_KEY:

        raise HTTPException(
            status_code=403,
            detail="Admin Key Required"
        )

    api_key = secrets.token_urlsafe(32)

    hashed = hash_key(api_key)

    conn = get_connection()

    try:

        conn.execute(
            """
            INSERT INTO api_keys
            (
                key_hash,
                user_name
            )

            VALUES (?,?)
            """,
            (
                hashed,
                request.user_name
            )
        )

        conn.commit()

    except sqlite3.IntegrityError:

        raise HTTPException(
            status_code=409,
            detail="Key Already Exists"
        )

    finally:

        conn.close()

    logger.info(
        f"Generated API Key For {request.user_name}"
    )

    return {

        "api_key": api_key,

        "user_name": request.user_name,

        "message": "Store This API Key Safely."

    }