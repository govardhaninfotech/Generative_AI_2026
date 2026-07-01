"""
Demo 06 — Role Prompting
PE Concept : Persona + expertise level changes depth, focus, and quality
Scenario   : Security audit, architecture review, interview prep
             Each role unlocks a different dimension of knowledge

Key insight: Role prompting is not just "act as X."
             The more specific the role, the more useful the output.
             Vague role → generic answer. Specific role → expert answer.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"


def ask(system: str, user: str) -> str:
    response = client.chat.completions.create(
        model    = MODEL,
        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature = 0.4
    )
    return response.choices[0].message.content


# The code they built in Day 2-3 — review it from multiple angles
THEIR_API_CODE = """
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import sqlite3, os

app = FastAPI()

def get_db():
    conn = sqlite3.connect("contacts.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

class ContactCreate(BaseModel):
    name: str
    phone: str

@app.post("/contacts")
def create_contact(data: ContactCreate, db = Depends(get_db)):
    db.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)",
               (data.name, data.phone))
    db.commit()
    return {"message": "created"}

@app.get("/contacts/{id}")
def get_contact(id: int, db = Depends(get_db)):
    row = db.execute("SELECT * FROM contacts WHERE id=?", (id,)).fetchone()
    if not row:
        raise HTTPException(404, "Not found")
    return dict(row)
"""

# ════════════════════════════════════════════════════
# PART A — Vague role vs specific role
# ════════════════════════════════════════════════════

VAGUE_ROLE = "You are an expert. Review this code."

SPECIFIC_ROLE = """
You are a OWASP Top 10 certified security engineer specialising in Python API security.
You have 8 years of experience finding vulnerabilities in FastAPI and Flask applications.
You think like an attacker first, then provide developer-friendly fixes.
Structure your findings as: VULNERABILITY → ATTACK SCENARIO → CVSS SCORE → FIX
"""

print("── Vague role ──")
print(ask(VAGUE_ROLE, f"Review:\n{THEIR_API_CODE}"))

print("\n── Specific security role ──")
print(ask(SPECIFIC_ROLE, f"Security audit:\n{THEIR_API_CODE}"))


# ════════════════════════════════════════════════════
# PART B — Multiple expert panels
# Same code reviewed by different specialists simultaneously
# ════════════════════════════════════════════════════

EXPERTS = {
    "Performance Engineer": """
        You are a backend performance engineer who optimises Python APIs for scale.
        You have profiled hundreds of FastAPI applications.
        Focus ONLY on performance: N+1 queries, connection pooling, caching opportunities,
        response time bottlenecks. Use metrics where possible.
        Format: ISSUE → IMPACT (ms/req) → FIX
    """,

    "DevOps / SRE": """
        You are an SRE responsible for deploying and maintaining Python APIs in production.
        Focus on: observability gaps, missing health checks, deployment risks,
        configuration management, graceful shutdown, and operational concerns.
        Think: "What will wake me up at 3am with this code?"
    """,

    "API Designer": """
        You are a REST API design expert who follows RFC standards.
        Focus on: HTTP verb correctness, status code accuracy, response schema consistency,
        versioning strategy, pagination, and API contract clarity.
        Reference specific RFCs or standards where relevant.
    """,

    "Junior Dev asking questions": """
        You are a curious junior developer seeing this code for the first time.
        Ask 5 genuine questions you would have about this code.
        Questions should be things a beginner would actually wonder about.
        Format: numbered questions only, no answers.
    """
}

print("\n" + "═" * 60)
print("MULTI-EXPERT PANEL REVIEW")
print("═" * 60)

for expert, role in EXPERTS.items():
    print(f"\n{'─'*50}")
    print(f" {expert}")
    print('─' * 50)
    print(ask(role, f"Review this API code:\n{THEIR_API_CODE}"))


# ════════════════════════════════════════════════════
# PART C — Role + Audience combination
# Same knowledge, different explanation style
# ════════════════════════════════════════════════════

TOPIC = "Explain what Dependency Injection does in our FastAPI contacts API"

AUDIENCES = {
    "CTO (non-technical)": """
        Explain to a non-technical CTO who cares about business impact.
        Use business language. No code. Focus on: reliability, maintainability, cost.
        Max 3 sentences.
    """,
    "Senior developer": """
        Explain to a senior developer who knows design patterns.
        Use technical terms freely. Compare to SOLID principles.
        Include a before/after code snippet.
    """,
    "Junior developer (day 1)": """
        Explain to someone on their first day of Python.
        Use a real-world analogy. Avoid jargon completely.
        Use simple language a 16-year-old could understand.
    """
}

print("\n" + "═" * 60)
print("SAME CONCEPT — DIFFERENT AUDIENCES")
print("═" * 60)
for audience, role in AUDIENCES.items():
    print(f"\n── For {audience} ──")
    print(ask(role, TOPIC))


# ── Teaching points ───────────────────────────────
# 1. Vague role → generic answer. Specific role → expert answer
# 2. Include: years of experience, specialisation, thinking style, output format
# 3. Role + audience is a powerful combination for documentation and teaching
# 4. In production: role prompts go in system prompt, audience in user message
# 5. You can run the same code through multiple expert roles in parallel (asyncio)
