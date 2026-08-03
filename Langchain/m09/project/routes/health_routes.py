from fastapi import APIRouter

from database import get_connection


router = APIRouter(
    tags=["Health"]
)


@router.get("/health")
def health():

    try:

        conn = get_connection()

        conn.execute(
            "SELECT 1"
        )

        conn.close()

        db = "connected"

    except Exception:

        db = "error"

    return {

        "status": "ok",

        "api": "running",

        "database": db

    }