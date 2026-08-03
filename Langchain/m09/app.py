"""
AI Chat Assistant
Streamlit + LangChain + Groq + SQLite + Logging

Run:
    streamlit run app.py
"""

import time
import sqlite3
import uuid
import logging

import streamlit as st

from logging.handlers import RotatingFileHandler

from langchain_groq import ChatGroq
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.output_parsers import (
    StrOutputParser,
    JsonOutputParser,
)
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
)


# =========================================================
# CONFIGURATION
# =========================================================

DB_PATH = "chat.db"
MODEL = "llama-3.3-70b-versatile"


# =========================================================
# STREAMLIT PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
)


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            "app.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        ),
    ],
)

logger = logging.getLogger(__name__)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():

    conn = get_connection()

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_message TEXT,
            ai_response TEXT,
            model_used TEXT,
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
            duration_ms REAL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );
        """
    )

    conn.commit()
    conn.close()


# =========================================================
# SAVE REQUEST LOG
# =========================================================

def save_request_log(request_id, session_id, duration):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO request_logs (
            request_id,
            session_id,
            duration_ms
        )
        VALUES (?, ?, ?)
        """,
        (
            request_id,
            session_id,
            round(duration, 2),
        ),
    )

    conn.commit()
    conn.close()


# =========================================================
# SAVE CHAT
# =========================================================

def save_chat(
    session_id,
    user_message,
    ai_response,
    model,
    duration,
):

    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT INTO chat_logs (
            session_id,
            user_message,
            ai_response,
            model_used,
            duration_ms
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            session_id,
            user_message,
            ai_response,
            model,
            duration,
        ),
    )

    conn.commit()

    chat_id = cursor.lastrowid

    conn.close()

    return chat_id


# =========================================================
# SAVE EVALUATION
# =========================================================

def save_eval(chat_id, scores):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO eval_logs (
            chat_log_id,
            relevance,
            coherence,
            conciseness,
            overall_score,
            eval_feedback
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            chat_id,
            scores.get("relevance", 0),
            scores.get("coherence", 0),
            scores.get("conciseness", 0),
            scores.get("overall", 0),
            scores.get("feedback", ""),
        ),
    )

    conn.commit()
    conn.close()


# =========================================================
# SAVE CONVERSATION MESSAGE
# =========================================================

def save_message(session_id, role, content):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO conversation_memory (
            session_id,
            role,
            content
        )
        VALUES (?, ?, ?)
        """,
        (
            session_id,
            role,
            content,
        ),
    )

    conn.commit()
    conn.close()


# =========================================================
# LOAD LANGCHAIN HISTORY
# =========================================================

def load_history(session_id):

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT role, content
        FROM conversation_memory
        WHERE session_id = ?
        ORDER BY id
        """,
        (session_id,),
    ).fetchall()

    conn.close()

    history = []

    for row in rows:

        if row["role"] == "user":

            history.append(
                HumanMessage(
                    content=row["content"]
                )
            )

        else:

            history.append(
                AIMessage(
                    content=row["content"]
                )
            )

    return history


# =========================================================
# LOAD CHAT FOR STREAMLIT UI
# =========================================================

def load_chat_messages(session_id):

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT role, content
        FROM conversation_memory
        WHERE session_id = ?
        ORDER BY id
        """,
        (session_id,),
    ).fetchall()

    conn.close()

    return [
        {
            "role": row["role"],
            "content": row["content"],
        }
        for row in rows
    ]


# =========================================================
# CREATE LLM
# =========================================================

def create_llms(api_key):

    llm = ChatGroq(
        api_key=api_key,
        model=MODEL,
        temperature=0.7,
        max_retries=3,
    )

    eval_llm = ChatGroq(
        api_key=api_key,
        model=MODEL,
        temperature=0.1,
        max_retries=3,
    )

    return llm, eval_llm


# =========================================================
# CREATE CHAINS
# =========================================================

def create_chains(api_key):

    llm, eval_llm = create_llms(api_key)

    system_prompt = """
    You are an expert AI assistant for a FastAPI
    and LangChain course.

    Be concise and helpful.
    """

    # Main Chat Chain
    chain = (
        ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),

                MessagesPlaceholder(
                    variable_name="history"
                ),

                ("human", "{input}"),
            ]
        )
        | llm
        | StrOutputParser()
    )

    # Evaluation Chain
    eval_chain = (
        ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an evaluator. Return ONLY JSON.",
                ),

                (
                    "human",
                    """
Evaluate the following answer.

Question:
{question}

Answer:
{answer}

Return ONLY this JSON format:

{{
    "relevance": 0.0,
    "coherence": 0.0,
    "conciseness": 0.0,
    "feedback": "..."
}}
""",
                ),
            ]
        )
        | eval_llm
        | JsonOutputParser()
    )

    return chain, eval_chain


# =========================================================
# GENERATE AI RESPONSE
# =========================================================

def generate_response(
    session_id,
    user_message,
    api_key,
):

    # -----------------------------------------------------
    # Generate unique request ID
    # -----------------------------------------------------

    request_id = str(uuid.uuid4())[:8]

    logger.info(
        f"[{request_id}] -> Chat request "
        f"| session={session_id}"
    )

    # -----------------------------------------------------
    # Load conversation history
    # -----------------------------------------------------

    history = load_history(session_id)

    # -----------------------------------------------------
    # Create chains
    # -----------------------------------------------------

    chain, eval_chain = create_chains(api_key)

    # -----------------------------------------------------
    # Start Timer
    # -----------------------------------------------------

    start = time.time()

    # -----------------------------------------------------
    # Call Groq LLM
    # -----------------------------------------------------

    reply = chain.invoke(
        {
            "input": user_message,
            "history": history,
        }
    )

    duration = (
        time.time() - start
    ) * 1000

    # -----------------------------------------------------
    # Save Conversation
    # -----------------------------------------------------

    save_message(
        session_id,
        "user",
        user_message,
    )

    save_message(
        session_id,
        "assistant",
        reply,
    )

    # -----------------------------------------------------
    # Save Chat Log
    # -----------------------------------------------------

    chat_id = save_chat(
        session_id,
        user_message,
        reply,
        MODEL,
        round(duration, 2),
    )

    # -----------------------------------------------------
    # Evaluate AI Response
    # -----------------------------------------------------

    eval_score = None

    try:

        scores = eval_chain.invoke(
            {
                "question": user_message,
                "answer": reply,
            }
        )

        relevance = float(
            scores.get("relevance", 0)
        )

        coherence = float(
            scores.get("coherence", 0)
        )

        conciseness = float(
            scores.get("conciseness", 0)
        )

        overall = round(
            (
                relevance
                + coherence
                + conciseness
            ) / 3,
            2,
        )

        scores["overall"] = overall

        save_eval(
            chat_id,
            scores,
        )

        eval_score = overall

    except Exception as error:

        logger.warning(
            f"[{request_id}] "
            f"Evaluation failed: {error}"
        )

    # -----------------------------------------------------
    # Save Request Log
    # -----------------------------------------------------

    save_request_log(
        request_id,
        session_id,
        duration,
    )

    logger.info(
        f"[{request_id}] <- Completed "
        f"| {duration:.0f}ms"
    )

    return {
        "reply": reply,
        "duration": round(duration, 2),
        "eval_score": eval_score,
        "request_id": request_id,
    }


# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_db()


# =========================================================
# SESSION STATE
# =========================================================

if "session_id" not in st.session_state:

    st.session_state.session_id = str(
        uuid.uuid4()
    )


if "messages" not in st.session_state:

       st.session_state.messages = (
        load_chat_messages(
            st.session_state.session_id
        )
    )


# =========================================================
# NEW CHAT FUNCTION
# =========================================================

def new_chat():

    st.session_state.session_id = str(
        uuid.uuid4()
    )

    st.session_state.messages = []


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🤖 AI Assistant")

    st.write(
        "Enter your Groq API key to start chatting."
    )

    # -----------------------------------------------------
    # API KEY INPUT
    # -----------------------------------------------------

    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Your Groq API key is used to communicate with the Groq API.",
    )

    if groq_api_key:

        st.success(
            "API Key Added"
        )

    else:

        st.warning(
            "API Key Required"
        )

    st.divider()

    # -----------------------------------------------------
    # CHAT ID
    # -----------------------------------------------------

    st.caption(
        "Current Chat ID"
    )

    st.code(
        st.session_state.session_id,
        language=None,
    )

    # -----------------------------------------------------
    # NEW CHAT
    # -----------------------------------------------------

    if st.button(
        "➕ New Chat",
        use_container_width=True,
    ):

        new_chat()

        st.rerun()

    st.divider()

    st.caption(
        f"Model: {MODEL}"
    )


# =========================================================
# MAIN UI
# =========================================================

st.title(
    "💬 AI Chat Assistant"
)

st.caption(
    "LangChain + Groq + SQLite + Logging"
)


# =========================================================
# API KEY MESSAGE
# =========================================================

if not groq_api_key:

    st.info(
        "👈 Enter your Groq API key in the sidebar "
        "to start chatting."
    )


# =========================================================
# DISPLAY EXISTING MESSAGES
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "Ask me anything...",
    disabled=not bool(groq_api_key),
)


# =========================================================
# PROCESS MESSAGE
# =========================================================

if prompt:

    # -----------------------------------------------------
    # Add User Message
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    # -----------------------------------------------------
    # Display User Message
    # -----------------------------------------------------

    with st.chat_message("user"):

        st.markdown(prompt)

    # -----------------------------------------------------
    # AI Response
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking..."
        ):

            try:

                result = generate_response(
                    st.session_state.session_id,
                    prompt,
                    groq_api_key,
                )

                answer = result["reply"]

                # -----------------------------------------
                # Display AI Answer
                # -----------------------------------------

                st.markdown(answer)

                # -----------------------------------------
                # Store in Streamlit Session
                # -----------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                # -----------------------------------------
                # Response Details
                # -----------------------------------------

                with st.expander(
                    "⚙️ Response Details"
                ):

                    st.write(
                        "Request ID:",
                        result["request_id"],
                    )

                    st.write(
                        "Session ID:",
                        st.session_state.session_id,
                    )

                    st.write(
                        "Model:",
                        MODEL,
                    )

                    st.write(
                        "Duration:",
                        f'{result["duration"]} ms',
                    )

                    st.write(
                        "Evaluation Score:",
                        result["eval_score"],
                    )

            # -------------------------------------------------
            # ERROR HANDLING
            # -------------------------------------------------

            except Exception as error:

                logger.exception(
                    "Chat generation failed"
                )

                st.error(
                    "Unable to generate response."
                )

                st.error(
                    str(error)
                )