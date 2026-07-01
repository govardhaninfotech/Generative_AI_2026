"""
Demo 09 — Temperature & LLM Parameters
PE Concept : Parameters change output behaviour — not just creativity
Scenario   : Same prompt, different parameters → radically different results
             Know which parameters to use for which task

Parameters covered:
  temperature   → randomness (0 = deterministic, 2 = chaotic)
  max_tokens    → output length limit
  top_p         → nucleus sampling (alternative to temperature)
  stop          → stop generation at specific tokens
  stream        → token by token vs all at once
"""

import os, time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"


def ask(user: str, system: str = "You are a helpful assistant.", **kwargs) -> str:
    response = client.chat.completions.create(
        model    = MODEL,
        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        **kwargs
    )
    return response.choices[0].message.content


# ════════════════════════════════════════════════════
# PART A — Temperature
# Run this multiple times — show how output changes
# ════════════════════════════════════════════════════

TEMP_PROMPT = "Write a one-sentence description of what our ContactsApp does."

print("═" * 60)
print("TEMPERATURE EXPERIMENT")
print("Same prompt, run 3 times at each temperature")
print("═" * 60)

for temp in [0.0, 0.7, 1.5]:
    print(f"\n── Temperature = {temp} ──")
    for i in range(3):
        result = ask(TEMP_PROMPT, temperature=temp)
        print(f"  Run {i+1}: {result}")


# ════════════════════════════════════════════════════
# PART B — Temperature by use case
# Show the right temperature for different tasks
# ════════════════════════════════════════════════════

USE_CASES = [
    (0.0,  "SQL query",        "Write a SQL query to get all contacts added in the last 7 days"),
    (0.1,  "JSON extraction",  "Extract: name=John Smith, phone=9876543210 as JSON"),
    (0.3,  "Code review",      "Review this function: def add(a,b): return a+b"),
    (0.7,  "Documentation",    "Write a README introduction for a contacts management API"),
    (1.2,  "Marketing copy",   "Write a tagline for ContactsApp"),
    (1.8,  "Brainstorming",    "Give me 5 unusual feature ideas for a contacts app"),
]

print("\n" + "═" * 60)
print("RIGHT TEMPERATURE FOR EACH TASK")
print("═" * 60)
for temp, task_type, prompt in USE_CASES:
    print(f"\n[temp={temp}] {task_type}")
    print(f"  {ask(prompt, temperature=temp)[:150]}")


# ════════════════════════════════════════════════════
# PART C — max_tokens
# Control response length — important for cost and UX
# ════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("MAX_TOKENS — Controlling response length")
print("═" * 60)

LONG_QUESTION = "Explain dependency injection in FastAPI with examples."

for max_tok in [50, 150, 500]:
    result = ask(LONG_QUESTION, temperature=0.3, max_tokens=max_tok)
    finish = " complete" if len(result.split()) < max_tok else " truncated"
    print(f"\n[max_tokens={max_tok}] {finish}")
    print(f"  {result[:200]}")


# ════════════════════════════════════════════════════
# PART D — stop sequences
# Stop generation at a specific token
# Critical for structured output and code generation
# ════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("STOP SEQUENCES — Stop at specific token")
print("═" * 60)

CODE_PROMPT = """
Write a Python function that validates a phone number.
Write ONLY the function. Stop after the closing line of the function.
"""

# Without stop sequence — may include explanation after code
without_stop = ask(CODE_PROMPT, temperature=0.1)
print("Without stop sequence:")
print(without_stop[:400])

# With stop — stops at blank line after function (cleaner for code extraction)
with_stop = ask(CODE_PROMPT, temperature=0.1, stop=["\n\n"])
print("\nWith stop='\\n\\n' (stops after function):")
print(with_stop[:400])


# ════════════════════════════════════════════════════
# PART E — Streaming
# Token by token — for chat UIs and long responses
# ════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("STREAMING — Token by token delivery")
print("═" * 60)

def stream_response(prompt: str):
    stream = client.chat.completions.create(
        model    = MODEL,
        messages = [{"role": "user", "content": prompt}],
        stream   = True,
        temperature = 0.5
    )
    print("Streaming: ", end="", flush=True)
    total_tokens = 0
    for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            print(token, end="", flush=True)
            total_tokens += 1
    print(f"\n[{total_tokens} tokens streamed]")

stream_response("Explain what streaming LLM responses means in 3 sentences.")


# ════════════════════════════════════════════════════
# CHEAT SHEET
# ════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("PARAMETER CHEAT SHEET")
print("═" * 60)
cheat_sheet = [
    ("temperature=0.0-0.2",  "SQL, JSON extraction, classification, structured output"),
    ("temperature=0.3-0.5",  "Code review, documentation, summarisation, Q&A"),
    ("temperature=0.6-0.9",  "Creative writing, explanations, chatbots"),
    ("temperature=1.0-2.0",  "Brainstorming, varied outputs, experimental"),
    ("max_tokens=50-200",    "Short answers, labels, classifications"),
    ("max_tokens=500-1000",  "Code snippets, explanations, reviews"),
    ("max_tokens=2000+",     "Long documents, full implementations"),
    ("stop=[\"\\n\"]",       "Single line outputs, labels"),
    ("stop=[\"\\n\\n\"]",   "Single paragraphs, functions"),
    ("stream=True",          "Chat UIs, long responses, progress feedback"),
]
for param, use_case in cheat_sheet:
    print(f"  {param:<28} → {use_case}")


# ── Teaching points ───────────────────────────────
# 1. temperature=0 does NOT mean identical output — just very similar
# 2. top_p and temperature — only change one at a time (Groq: use temperature)
# 3. max_tokens affects cost — always set it, never leave unlimited
# 4. stop sequences are underused — powerful for code extraction
# 5. stream=True is a generator — connect back to Day 1 generators
