import hashlib

from fastapi import Header
from fastapi import HTTPException

from database import get_connection


# ======================================================
# Hash API Key
# ======================================================

def hash_key(key: str) -> str:
    """
    Convert API key into SHA256 Hash
    """

    return hashlib.sha256(
        key.encode()
    ).hexdigest()


# ======================================================
# Verify API Key
# ======================================================

async def verify_api_key(
        x_api_key: str = Header(...)
):

    hashed_key = hash_key(x_api_key)

    conn = get_connection()

    row = conn.execute(

        """
        SELECT user_name
        FROM api_keys
        WHERE key_hash=?
        AND is_active=1
        """,

        (hashed_key,)

    ).fetchone()

    conn.close()

    if row is None:

        raise HTTPException(
            status_code=403,
            detail="Invalid or Missing API Key"
        )

    return row["user_name"]