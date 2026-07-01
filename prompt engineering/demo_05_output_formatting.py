"""
Demo 05 — Output Formatting
PE Concept : Force strict output format — JSON, markdown, schema
Scenario   : Generate API docs, structured reports, typed responses
             your downstream code can parse reliably

Key insight: An LLM response your code can't parse is useless.
             Formatting prompts = the bridge between AI and your system.
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
        temperature = 0.1
    )
    return response.choices[0].message.content


def ask_json(system: str, user: str) -> dict:
    """Ask and parse JSON response."""
    result = ask(system, user)
    # Strip markdown code blocks if model wraps in ```json
    result = result.strip()
    print(result)
    if result.startswith("```"):
        result = result.split("```")[1] 
        if result.startswith("json"):
            result = result[4:]  
    return json.loads(result.strip())

# ════════════════════════════════════════════════════
# PART A — API Documentation Generator
# Input: raw function signature + docstring
# Output: structured OpenAPI-compatible JSON
# ════════════════════════════════════════════════════

API_DOC_SYSTEM = """
You are an API documentation generator.
Given a Python function, return ONLY a JSON object with this exact schema:
{
  "endpoint": "string — the route path",
  "method": "GET|POST|PUT|DELETE|PATCH",
  "summary": "string — one line description",
  "description": "string — detailed description",
  "parameters": [{"name": "string", "in": "path|query|body", "type": "string", "required": true|false, "description": "string"}],
  "responses": {
    "200": {"description": "string", "schema": {}},
    "400": {"description": "string"},
    "404": {"description": "string"}
  },
  "tags": ["string"]
}
Return ONLY the JSON. No explanation. No markdown fences.
"""

FUNCTION_CODE = """
@app.get("/users/{user_id}/orders")
def get_user_orders(
    user_id: int,
    status: str = None,
    limit: int = 10,
    offset: int = 0
):
    \"\"\"
    Retrieve paginated orders for a specific user.
    Optionally filter by order status.
    Returns 404 if user not found.
    \"\"\"
    pass
"""

print("═" * 60)
print("API DOCUMENTATION GENERATOR")
print("═" * 60)
doc = ask_json(API_DOC_SYSTEM, f"Generate docs for:\n{FUNCTION_CODE}")
print(json.dumps(doc, indent=2))


# ════════════════════════════════════════════════════
# PART B — Code Review Report Generator
# Structured markdown output for PR reviews
# ════════════════════════════════════════════════════

CODE_REVIEW_SYSTEM = """
You are a senior code reviewer. Generate a structured PR review report.

Output format — use EXACTLY this markdown structure:

## Summary
[2-3 sentence overall assessment]

## Issues Found

###  Critical
[List critical issues — must fix before merge]

###  Medium  
[List medium issues — should fix]

###  Low
[List low issues — nice to have]

## Security Concerns
[Any security-related observations]

## Performance Notes
[Any performance-related observations]

## Verdict
**[APPROVE | REQUEST CHANGES | NEEDS DISCUSSION]** — [one sentence reason]
"""

PR_CODE = """
@app.post("/login")
def login(username: str, password: str):
    user = db.execute(f"SELECT * FROM users WHERE username='{username}'").fetchone()
    if user and user['password'] == password:
        token = username + "_token_" + str(time.time())
        return {"token": token}
    return {"error": "invalid credentials"}
"""

print("\n" + "═" * 60)
print("STRUCTURED CODE REVIEW REPORT")
print("═" * 60)
print(ask(CODE_REVIEW_SYSTEM, f"Review this code:\n{PR_CODE}"))


# ════════════════════════════════════════════════════
# PART C — Database Schema Generator
# Natural language → SQL CREATE TABLE statements
# ════════════════════════════════════════════════════

SCHEMA_SYSTEM = """
You are a database architect. Convert requirements to SQL.

Return a JSON object with this structure:
{
  "tables": [
    {
      "name": "table_name",
      "sql": "CREATE TABLE ... full SQL statement",
      "description": "what this table stores",
      "relationships": ["table_name — relationship description"]
    }
  ],
  "indexes": ["CREATE INDEX statements"],
  "notes": ["important design decisions made"]
}
Return ONLY JSON. No markdown.
"""

REQUIREMENTS = """
Build a database for a project management app:
- Users can create projects
- Projects have multiple tasks
- Tasks can be assigned to users
- Tasks have status (todo, in_progress, done) and priority (low, medium, high)
- Users can comment on tasks
- Track when things were created and updated
"""

print("\n" + "═" * 60)
print("DATABASE SCHEMA GENERATOR")
print("═" * 60)
schema = ask_json(SCHEMA_SYSTEM, REQUIREMENTS)
for table in schema.get("tables", []):
    print(f"\n {table['name']}: {table['description']}")
    print(table['sql'])
print("\n Design notes:")
for note in schema.get("notes", []):
    print(f"  • {note}")


# ── Teaching points ───────────────────────────────
# 1. "Return ONLY JSON" — the most important instruction for parseable output
# 2. Always strip markdown fences — models wrap JSON in ```json sometimes
# 3. Show the schema in the prompt — reduces hallucinated field names
# 4. temperature=0.1 for structured output — consistency over creativity
# 5. In production: validate parsed JSON against Pydantic model immediately
# 6. Next step from here → function calling (Demo 07) which enforces schema at API level
