from fastapi import FastAPI
from routes.stream_routes import router as stream_router
from auth import hash_key
from config import ADMIN_KEY
from database import get_connection, init_db
from middleware import logging_middleware, logger
from routes.auth_routes import router as auth_router
from routes.chat_routes import router as chat_router
from routes.log_routes import router as log_router
from routes.health_routes import router as health_router

# =====================================================
# FastAPI Application
# =====================================================

app = FastAPI(title="AI Chat API", version="1.0.0")


# =====================================================
# Startup Event
# =====================================================


@app.on_event("startup")
def startup():

    init_db()

    conn = get_connection()

    count = conn.execute("""
        SELECT COUNT(*)

        FROM api_keys
        """).fetchone()[0]

    if count == 0:

        conn.execute(
            """
            INSERT INTO api_keys(key_hash,user_name)VALUES (?,?)
            """,
            (hash_key(ADMIN_KEY), "admin"),
        )
        conn.commit()
        logger.info("Admin API Key Seeded")
    conn.close()


# =====================================================
# Middleware
# =====================================================

app.middleware("http")(logging_middleware)


# =====================================================
# Register Routes
# =====================================================
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(log_router)
app.include_router(health_router)
app.include_router(stream_router)
