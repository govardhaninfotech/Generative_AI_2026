import time
import uuid
import logging

from logging.handlers import RotatingFileHandler

from fastapi import Request

from config import (
    LOG_FILE,
    LOG_MAX_SIZE,
    LOG_BACKUP_COUNT
)

from database import save_request_log


# ==========================================================
# Logging Configuration
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_SIZE,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
    ]
)

logger = logging.getLogger(__name__)


# ==========================================================
# Request Logging Middleware
# ==========================================================

async def logging_middleware(
        request: Request,
        call_next
):

    request_id = str(uuid.uuid4())[:8]

    session_id = request.headers.get(
        "X-Session-ID",
        "unknown"
    )

    api_key = request.headers.get(
        "X-API-Key",
        "none"
    )

    user_key = api_key[:8] + "..."

    logger.info(
        f"[{request_id}] -> {request.method} {request.url.path}"
    )

    start_time = time.time()

    response = await call_next(request)

    duration = (time.time() - start_time) * 1000

    logger.info(
        f"[{request_id}] <- {response.status_code} | {duration:.0f} ms"
    )

    save_request_log(
        request_id=request_id,
        session_id=session_id,
        user_key=user_key,
        endpoint=str(request.url.path),
        method=request.method,
        status_code=response.status_code,
        duration=duration
    )

    response.headers["X-Request-ID"] = request_id

    return response