"""
Demo 04 — Chain of Thought (CoT)
PE Concept : Force step-by-step reasoning before the final answer
Scenario   : Debug a complex production bug + system design decisions
             where wrong reasoning = expensive mistakes

Key insight: LLMs make fewer mistakes when forced to reason step by step.
             "Think step by step" is not magic — it forces the model to
             allocate tokens to reasoning before committing to an answer.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"


def ask(system: str, user: str, temperature: float = 0.3) -> str:
    response = client.chat.completions.create(
        model    = MODEL,
        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature = temperature
    )
    return response.choices[0].message.content


# ════════════════════════════════════════════════════
# PART A — Bug debugging with and without CoT
# ════════════════════════════════════════════════════

BUGGY_CODE = """
from fastapi import FastAPI, Depends
import sqlite3

app = FastAPI()

def get_db():
    conn = sqlite3.connect("app.db")
    yield conn

@app.get("/users/{user_id}")
def get_user(user_id: int, db = Depends(get_db)):
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id).fetchone()
    if not user:
        return {"error": "not found"}
    return dict(user)

@app.post("/users")
def create_user(data: dict, db = Depends(get_db)):
    db.execute("INSERT INTO users (name, email) VALUES (?, ?)",
               (data["name"], data["email"]))
    return {"message": "created"}
"""

# Without CoT — jumps to answer
NO_COT = """
You are a senior FastAPI developer.
Review the code and tell me what bugs it has.
"""

# With CoT — forced to reason step by step
WITH_COT = """
You are a senior FastAPI developer doing a thorough code review.

Follow this EXACT process:
1. UNDERSTAND: Read the code carefully and describe what it does
2. ANALYSE EACH FUNCTION: Go through each route one by one
3. IDENTIFY ISSUES: For each issue found, explain WHY it is a problem
4. SEVERITY RATING: Rate each issue (CRITICAL / HIGH / MEDIUM / LOW)
5. FIXES: Provide corrected code for each issue
6. SUMMARY: List all issues found in order of severity

Do not skip any step. Show your full reasoning.
"""

print("═" * 60)
print("WITHOUT Chain of Thought")
print("═" * 60)
print(ask(NO_COT, f"Review this code:\n{BUGGY_CODE}"))

print("\n" + "═" * 60)
print("WITH Chain of Thought")
print("═" * 60)
print(ask(WITH_COT, f"Review this code:\n{BUGGY_CODE}"))


# ════════════════════════════════════════════════════
# PART B — Architecture decision with CoT
# Real scenario: choosing between two approaches
# Wrong decision = months of rework
# ════════════════════════════════════════════════════

ARCH_QUESTION = """
We are building a notification system.
Users can receive notifications via email, SMS, and push.
Expected load: 100,000 notifications per day.
Current stack: FastAPI, PostgreSQL, Redis.

Option A: Send notifications synchronously inside the API request
Option B: Push to a queue (Redis) and process with background workers

Which should we choose?
"""

ARCH_COT_SYSTEM = """
You are a solutions architect with experience in high-load systems.

When answering architecture questions, always follow this framework:
1. REQUIREMENTS ANALYSIS: What are the key constraints and goals?
2. OPTION A EVALUATION: Pros, cons, failure modes, scalability limits
3. OPTION B EVALUATION: Pros, cons, failure modes, scalability limits
4. COMPARISON TABLE: Side by side on: latency, reliability, complexity, cost
5. RECOMMENDATION: Clear choice with justification
6. IMPLEMENTATION NOTES: Key things to watch out for in the chosen approach

Be specific. Use numbers where possible. Do not be vague.
"""

print("\n" + "═" * 60)
print("ARCHITECTURE DECISION WITH CHAIN OF THOUGHT")
print("═" * 60)
print(ask(ARCH_COT_SYSTEM, ARCH_QUESTION, temperature=0.2))


# ════════════════════════════════════════════════════
# PART C — Self-check CoT
# Ask the model to verify its own answer
# Reduces hallucination significantly
# ════════════════════════════════════════════════════

SELF_CHECK_SYSTEM = """
You are a senior developer. When answering:
1. Give your answer
2. Then under "SELF-CHECK:", verify your answer by asking:
   - Are there any edge cases I missed?
   - Could this fail in production?
   - Is there a simpler solution?
3. Revise your answer if the self-check reveals issues
"""

SQL_QUESTION = """
Write a SQL query to find the top 5 users who have placed the most orders
in the last 30 days, along with their total order value.
Tables: users(id, name, email), orders(id, user_id, amount, created_at)
"""

print("\n" + "═" * 60)
print("SELF-CHECK CoT — Verify own answer")
print("═" * 60)
print(ask(SELF_CHECK_SYSTEM, SQL_QUESTION, temperature=0.1))


# ── Teaching points ───────────────────────────────
# 1. CoT is not magic — it allocates more tokens to reasoning
# 2. More reasoning tokens = fewer logical errors
# 3. Use CoT for: debugging, architecture, SQL, algorithms
# 4. Skip CoT for: simple extraction, classification, summarisation
# 5. Self-check CoT is powerful — model catches its own mistakes
# 6. In production: CoT costs more tokens but saves debugging time
