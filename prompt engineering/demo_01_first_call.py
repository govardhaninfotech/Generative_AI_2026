"""
Demo 01 — First Groq API Call
PE Concept : Basic connection, message structure, roles
Scenario   : Understand the message array that drives every LLM interaction

Install    : pip install groq python-dotenv
API Key    : console.groq.com → free tier
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"   # fast, free, powerful


# ════════════════════════════════════════════════════
# PART A — Bare minimum call
# ════════════════════════════════════════════════════

def simple_call(user_message: str) -> str:
    response = client.chat.completions.create(
        model    = MODEL,
        messages = [
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content


# ════════════════════════════════════════════════════
# PART B — Inspect the full response object
# What does the API actually return?
# ════════════════════════════════════════════════════

def call_with_metadata(user_message: str):
    response = client.chat.completions.create(
        model    = MODEL,
        messages = [{"role": "user", "content": user_message}]
    )

    print("═" * 50)
    print(f"Model      : {response.model}")
    print(f"Finish     : {response.choices[0].finish_reason}")
    print(f"Prompt tok : {response.usage.prompt_tokens}")
    print(f"Output tok : {response.usage.completion_tokens}")
    print(f"Total tok  : {response.usage.total_tokens}")
    print("─" * 50)
    print(f"Response   :\n{response.choices[0].message.content}")
    print("═" * 50)


# ════════════════════════════════════════════════════
# PART C — The message array structure
# This is the most important concept in the whole session
# Every LLM framework (LangChain, LlamaIndex etc) builds on this
# ════════════════════════════════════════════════════

def explain_message_roles():
    """
    Three roles in the message array:
      system    → sets behaviour, persona, constraints (you control this)
      user      → what the human says
      assistant → what the LLM replied (used for history)

    The model ONLY knows what is in this array.
    It has no memory beyond what you pass in.
    """
    messages = [
        {
            "role"   : "system",
            "content": "You are a senior Python developer. Be concise. Always give code examples."
        },
        {
            "role"   : "user",
            "content": "What is a context manager?"
        }
    ]

    response = client.chat.completions.create(model=MODEL, messages=messages)
    print(response.choices[0].message.content)


# ════════════════════════════════════════════════════
# RUN
# ════════════════════════════════════════════════════

if __name__ == "__main__":

    print("\n── PART A: Simple call ──")
    print(simple_call("What is an API in one sentence?"))

    print("\n── PART B: Full response metadata ──")
    call_with_metadata("What is REST?")

    print("\n── PART C: Message roles ──")
    explain_message_roles()

# ── Teaching points ───────────────────────────────
# 1. The message array is EVERYTHING — LangChain, agents, RAG all build on it
# 2. response.usage → token counts → this is how you're billed
# 3. finish_reason → "stop" = normal, "length" = hit max_tokens, "tool_calls" = agent used a tool
# 4. The model has ZERO memory — every call is stateless
#    If you want memory → you manage the messages array yourself
