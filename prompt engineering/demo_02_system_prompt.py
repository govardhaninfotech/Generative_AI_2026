"""
Demo 02 — System Prompt Power
PE Concept : System prompt controls persona, tone, constraints, output format
Scenario   : Same question — wildly different answers based on system prompt

Key insight: The system prompt is YOUR code. It runs before every user message.
             In a production AI app, users never see or modify it.
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
        ]
    )
    return response.choices[0].message.content


USER_QUESTION = "How should I handle errors in my API?"

# ════════════════════════════════════════════════════
# PART A — No system prompt vs with system prompt
# ════════════════════════════════════════════════════

NO_SYSTEM = ""

SENIOR_DEV = """
You are a senior backend engineer with 10 years of FastAPI experience.
Give practical, production-ready advice.
Always include code examples.
Be direct — no fluff.
"""

print("── No system prompt ──")
print(ask(NO_SYSTEM, USER_QUESTION))

print("\n── Senior dev system prompt ──")
print(ask(SENIOR_DEV, USER_QUESTION))


# ════════════════════════════════════════════════════
# PART B — Same question, different personas
# Shows how system prompt completely changes the response
# ════════════════════════════════════════════════════

PERSONAS = {
    "Strict code reviewer": """
        You are a strict code reviewer. Be critical.
        Point out every potential issue.
        Format: numbered list of problems, each with a severity (LOW/MEDIUM/HIGH).
        Do not sugarcoat anything.
    """,

    "Junior dev mentor": """
        You are mentoring a junior developer.
        Use simple language. Use analogies.
        Encourage them. Avoid jargon.
        Max 3 bullet points per answer.
    """,

    "Security auditor": """
        You are a cybersecurity expert reviewing API code.
        Focus ONLY on security implications.
        Format your response as:
        VULNERABILITIES: (list)
        RISKS: (list)
        FIXES: (list)
        Always assume the worst-case attacker scenario.
    """,

    "Tech lead in a hurry": """
        You are a tech lead in a standup meeting.
        Be extremely brief. Max 2 sentences.
        Give the most critical point only.
        No pleasantries.
    """
}


print("\n" + "═" * 60)
print("SAME QUESTION — DIFFERENT PERSONAS")
print("═" * 60)

for persona, system_prompt in PERSONAS.items():
    print(f"\n── {persona} ──")
    print(ask(system_prompt, USER_QUESTION))
    print()


# ════════════════════════════════════════════════════
# PART C — System prompt with CONSTRAINTS
# Controlling what the model CAN and CANNOT do
# Critical for production apps
# ════════════════════════════════════════════════════

CONSTRAINED = """
You are a customer support assistant for a FastAPI course.

RULES:
- ONLY answer questions about FastAPI, Python, and REST APIs
- If asked about anything else, say: "I can only help with FastAPI and Python questions."
- Never write more than 150 words
- Always end with: "Need more help? Check our docs at docs.example.com"
- Never mention competitor frameworks (Flask, Django, Express)
"""

print("── Constrained system prompt ──")
print(ask(CONSTRAINED, "How do I add authentication to my FastAPI app?"))

print("\n── Trying to break the constraint ──")
print(ask(CONSTRAINED, "What is the capital of France?"))

print("\n── Trying to get it to mention Flask ──")
print(ask(CONSTRAINED, "Is FastAPI better than Flask?"))


# ── Teaching points ───────────────────────────────
# 1. System prompt = your business logic in plain English
# 2. It runs invisibly before every user message
# 3. Constraints are not 100% reliable — don't use as security layer
#    Use it for behaviour shaping, not security enforcement
# 4. In production: system prompt is secret, users never see it
# 5. In LangChain: SystemMessage("...") maps to this exactly
