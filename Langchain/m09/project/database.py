import sqlite3

from langchain_core.messages import HumanMessage, AIMessage

from config import DB_PATH


# =====================================================
# Database Connection
# =====================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================================
# Create Database Tables
# =====================================================

def init_db():

    conn = get_connection()

    conn.executescript("""

    CREATE TABLE IF NOT EXISTS api_keys (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        key_hash TEXT NOT NULL UNIQUE,

        user_name TEXT NOT NULL,

        is_active INTEGER NOT NULL DEFAULT 1,

        created_at TEXT DEFAULT (datetime('now'))

    );


    CREATE TABLE IF NOT EXISTS chat_logs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        session_id TEXT,

        user_key TEXT,

        user_message TEXT,

        ai_response TEXT,

        model_used TEXT,

        prompt_tokens INTEGER DEFAULT 0,

        output_tokens INTEGER DEFAULT 0,

        duration_ms REAL DEFAULT 0,

        created_at TEXT DEFAULT (datetime('now'))

    );


    CREATE TABLE IF NOT EXISTS eval_logs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        chat_log_id INTEGER,

        relevance REAL,

        coherence REAL,

        conciseness REAL,

        overall_score REAL,

        eval_feedback TEXT,

        created_at TEXT DEFAULT (datetime('now'))

    );


    CREATE TABLE IF NOT EXISTS conversation_memory (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        session_id TEXT,

        role TEXT,

        content TEXT,

        created_at TEXT DEFAULT (datetime('now'))

    );


    CREATE TABLE IF NOT EXISTS request_logs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        request_id TEXT,

        session_id TEXT,

        user_key TEXT,

        endpoint TEXT,

        method TEXT,

        status_code INTEGER,

        duration_ms REAL,

        created_at TEXT DEFAULT (datetime('now'))

    );

    """)

    conn.commit()

    conn.close()
    
# =====================================================
# Save Request Log
# =====================================================

def save_request_log(
        request_id,
        session_id,
        user_key,
        endpoint,
        method,
        status_code,
        duration):

    conn = get_connection()

    conn.execute(

        """
        INSERT INTO request_logs
        (
            request_id,
            session_id,
            user_key,
            endpoint,
            method,
            status_code,
            duration_ms
        )

        VALUES (?,?,?,?,?,?,?)
        """,

        (
            request_id,
            session_id,
            user_key,
            endpoint,
            method,
            status_code,
            round(duration, 2)
        )

    )

    conn.commit()

    conn.close()
# =====================================================
# Save Chat
# =====================================================

def save_chat(
        session_id,
        user_key,
        user_message,
        ai_response,
        model,
        prompt_tokens,
        output_tokens,
        duration):

    conn = get_connection()

    cursor = conn.execute(

        """
        INSERT INTO chat_logs
        (
            session_id,
            user_key,
            user_message,
            ai_response,
            model_used,
            prompt_tokens,
            output_tokens,
            duration_ms
        )

        VALUES (?,?,?,?,?,?,?,?)
        """,

        (
            session_id,
            user_key,
            user_message,
            ai_response,
            model,
            prompt_tokens,
            output_tokens,
            duration
        )

    )

    conn.commit()

    chat_id = cursor.lastrowid

    conn.close()

    return chat_id
# =====================================================
# Save Evaluation
# =====================================================

def save_eval(chat_id, score):

    conn = get_connection()

    cursor = conn.execute(

        """
        INSERT INTO eval_logs
        (
            chat_log_id,
            relevance,
            coherence,
            conciseness,
            overall_score,
            eval_feedback
        )

        VALUES (?,?,?,?,?,?)
        """,

        (
            chat_id,
            score.get("relevance", 0),
            score.get("coherence", 0),
            score.get("conciseness", 0),
            score.get("overall", 0),
            score.get("feedback", "")
        )

    )

    conn.commit()

    eval_id = cursor.lastrowid

    conn.close()

    return eval_id
# =====================================================
# Load Conversation History
# =====================================================

def load_history(session_id):

    conn = get_connection()

    rows = conn.execute(

        """
        SELECT role, content
        FROM conversation_memory
        WHERE session_id=?
        ORDER BY id
        """,

        (session_id,)

    ).fetchall()

    conn.close()

    history = []

    for row in rows:

        if row["role"] == "user":

            history.append(
                HumanMessage(content=row["content"])
            )

        else:

            history.append(
                AIMessage(content=row["content"])
            )

    return history
# =====================================================
# Save Conversation
# =====================================================

def save_message(session_id, role, content):

    conn = get_connection()

    conn.execute(

        """
        INSERT INTO conversation_memory
        (
            session_id,
            role,
            content
        )

        VALUES (?,?,?)
        """,

        (
            session_id,
            role,
            content
        )

    )

    conn.commit()

    conn.close()