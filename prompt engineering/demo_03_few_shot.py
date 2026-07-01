"""
Demo 03 — Zero-shot vs Few-shot
PE Concept : Examples dramatically improve output consistency and format
Scenario   : Extract structured data from messy unstructured text
             (real world: parsing user feedback, tickets, emails)

Key insight: Few-shot = teaching by example inside the prompt.
             Cheaper than fine-tuning. More flexible than regex.
"""

import os, json
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
        temperature = 0.1   # low temp for extraction tasks
    )
    return response.choices[0].message.content


# ════════════════════════════════════════════════════
# REAL WORLD SCENARIO
# You receive bug reports in plain text from users
# You need to extract structured data for your ticket system
# ════════════════════════════════════════════════════

BUG_REPORTS = [
    "Hey the login page is completely broken on my iPhone 14, Safari browser. I click submit and nothing happens. This started yesterday around 3pm. Very urgent, I have a demo tomorrow!",
    "getting 500 error when i try to upload files larger than 10mb. tested on chrome and firefox both same issue. not urgent but annoying",
    "The dashboard charts dont load in Firefox 119 but work fine in Chrome. Low priority. Happens since last Tuesday's deployment.",
]


# ── ZERO-SHOT — just tell it what to do, no examples ──────────
ZERO_SHOT_SYSTEM = """
Extract bug report details and return a JSON object with these fields:
severity, browser, device, description, reported_since
"""

print("═" * 60)
print("ZERO-SHOT — No examples given")
print("═" * 60)
for report in BUG_REPORTS:
    print(f"\nInput: {report[:60]}...")
    result = ask(ZERO_SHOT_SYSTEM, report)
    print(f"Output: {result}")


# ── FEW-SHOT — give examples to teach the exact format ────────
FEW_SHOT_SYSTEM = """
Extract bug report details and return ONLY a JSON object.
No explanation. No markdown. Just the raw JSON.

Examples:

Input: "App crashes on Android 12 when opening settings, Chrome browser. Critical issue, production is down!"
Output: {"severity": "critical", "browser": "Chrome", "device": "Android 12", "description": "App crashes when opening settings", "reported_since": "unknown"}

Input: "Minor UI glitch on the profile page, text overlaps on small screens. Using Safari on MacBook. Noticed last week."
Output: {"severity": "low", "browser": "Safari", "device": "MacBook", "description": "Text overlaps on small screens on profile page", "reported_since": "last week"}

Now extract from the input below. Return ONLY JSON, nothing else.
"""

print("\n" + "═" * 60)
print("FEW-SHOT — With examples")
print("═" * 60)

extracted = []
for report in BUG_REPORTS:
    print(f"\nInput: {report[:60]}...")
    result = ask(FEW_SHOT_SYSTEM, report)
    print(f"Output: {result}")
    try:
        parsed = json.loads(result)
        extracted.append(parsed)
        print(f"Valid JSON — severity: {parsed.get('severity')}")
    except json.JSONDecodeError:
        print("Not valid JSON — few-shot needs more examples")

print(f"\n Successfully parsed {len(extracted)}/{len(BUG_REPORTS)} reports")


# ════════════════════════════════════════════════════
# PART B — Classification with few-shot
# Support ticket routing
# ════════════════════════════════════════════════════

CLASSIFIER_SYSTEM = """
Classify the support ticket into exactly one category.
Return ONLY the category name. Nothing else.

Categories: BUG | FEATURE_REQUEST | BILLING | ACCOUNT | GENERAL

Examples:
Ticket: "I can't log in, my password reset email never arrived" → ACCOUNT
Ticket: "The export button doesn't work in Firefox" → BUG
Ticket: "Can you add dark mode to the dashboard?" → FEATURE_REQUEST
Ticket: "I was charged twice this month" → BILLING
Ticket: "How do I share a project with my team?" → GENERAL
"""

TICKETS = [
    "The API returns 404 for endpoints that worked last week",
    "Would love if we could filter reports by date range",
    "My invoice shows the wrong company name",
    "Getting a blank screen after logging in on Chrome",
    "What's the maximum file size I can upload?",
]

print("\n" + "═" * 60)
print("FEW-SHOT CLASSIFIER — Ticket routing")
print("═" * 60)
for ticket in TICKETS:
    category = ask(CLASSIFIER_SYSTEM, ticket)
    print(f"  [{category.strip():16}] {ticket}")


# ── Teaching points ───────────────────────────────
# 1. Zero-shot → inconsistent format, hallucinated fields
# 2. Few-shot  → consistent JSON, correct fields every time
# 3. Rule of thumb: 2-5 examples is usually enough
# 4. Examples must COVER EDGE CASES — not just happy path
# 5. temperature=0.1 for extraction — you want consistency not creativity
# 6. This replaces complex regex parsers in real apps
