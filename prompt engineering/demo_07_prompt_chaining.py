"""
Demo 07 — Prompt Chaining
PE Concept : Output of one prompt becomes input of the next
Scenario   : PR workflow — code → review → test cases → commit message → changelog
             Each step adds value, builds on the previous

Key insight: Complex tasks broken into focused steps = better quality
             than one giant prompt trying to do everything.
             This is the conceptual foundation of LangChain pipelines.
"""

import os, json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"


def ask(system: str, user: str, temperature: float = 0.2) -> str:
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
# THE CHAIN
# Input: a new feature's code
# Step 1 → code review
# Step 2 → extract issues as JSON
# Step 3 → generate test cases for the issues
# Step 4 → write commit message
# Step 5 → update changelog entry
# ════════════════════════════════════════════════════

NEW_FEATURE_CODE = """
@app.post("/contacts/bulk")
def bulk_create(contacts: list[dict]):
    \"\"\"Create multiple contacts at once.\"\"\"
    created = []
    for contact in contacts:
        db.execute(
            "INSERT INTO contacts (name, phone) VALUES (?, ?)",
            (contact["name"], contact["phone"])
        )
        created.append(contact)
    db.commit()
    return {"created": len(created), "contacts": created}
"""

print(" PROMPT CHAIN — PR Workflow Automation")
print("=" * 60)
print(f"Input code:\n{NEW_FEATURE_CODE}")
print("=" * 60)


# ── STEP 1: Code Review ───────────────────────────────────────
print("\n STEP 1: Code Review")
step1_system = """
You are a senior FastAPI developer doing a code review.
Be concise. List issues clearly.
Format each issue as: [SEVERITY] Description
Severities: CRITICAL | HIGH | MEDIUM | LOW
"""
step1_result = ask(step1_system, f"Review this code:\n{NEW_FEATURE_CODE}")
print(step1_result)


# ── STEP 2: Extract Issues as JSON (feeds Step 3) ────────────
print("\n  STEP 2: Structuring issues as JSON")
step2_system = """
Convert the code review into a JSON array.
Each item: {"severity": string, "issue": string, "line": string or null}
Return ONLY JSON array. No markdown.
"""
step2_result = ask(step2_system, f"Code review to convert:\n{step1_result}")
print(step2_result)

try:
    issues = json.loads(step2_result)
    print(f" Parsed {len(issues)} issues")
except:
    issues = []
    print("  JSON parse failed — continuing with raw text")


# ── STEP 3: Generate Test Cases ───────────────────────────────
print("\n  STEP 3: Generating test cases")
step3_system = """
You are a senior QA engineer writing pytest test cases.
Generate test cases that specifically target the issues found in the review.
Include: happy path, edge cases, and cases for each identified issue.
Use FastAPI TestClient.
"""
step3_input = f"""
Code being tested:
{NEW_FEATURE_CODE}

Issues found in review:
{step2_result}

Write pytest test cases.
"""
step3_result = ask(step3_system, step3_input, temperature=0.1)
print(step3_result)


# ── STEP 4: Commit Message ────────────────────────────────────
print("\n  STEP 4: Writing commit message")
step4_system = """
Write a git commit message following Conventional Commits specification.
Format:
type(scope): subject

body (what and why, not how)

BREAKING CHANGE: (if any)
Fixes: (issue numbers if mentioned)

Types: feat|fix|docs|style|refactor|test|chore
Be specific. Max 72 chars for subject line.
"""
step4_input = f"""
New feature added:
{NEW_FEATURE_CODE}

Issues identified:
{step1_result}
"""
step4_result = ask(step4_system, step4_input, temperature=0.1)
print(step4_result)


# ── STEP 5: Changelog Entry ───────────────────────────────────
print("\n  STEP 5: Changelog entry")
step5_system = """
Write a CHANGELOG.md entry for this feature.
Follow Keep a Changelog format (keepachangelog.com).
Format:
### Added
- ...

### Fixed (if applicable)
- ...

### Security (if applicable)
- ...

Be user-facing — write for the person using the API, not the developer.
"""
step5_input = f"""
Feature: bulk contact creation endpoint
Commit: {step4_result}
Issues addressed: {step1_result}
"""
step5_result = ask(step5_system, step5_input, temperature=0.2)
print(step5_result)


# ── FINAL OUTPUT ──────────────────────────────────────────────
print("\n" + "=" * 60)
print(" CHAIN COMPLETE — Full PR package generated:")
print("  Step 1 → Code review")
print("  Step 2 → Structured issues (JSON)")
print("  Step 3 → Test cases (pytest)")
print("  Step 4 → Commit message (Conventional Commits)")
print("  Step 5 → Changelog entry (Keep a Changelog)")
print("=" * 60)
print("\n In LangChain this chain becomes:")
print("   review_chain | extract_chain | test_chain | commit_chain | changelog_chain")
print("   One line. Same logic. That's Module 10.")


# ── Teaching points ───────────────────────────────
# 1. Each step is focused → better quality than one mega-prompt
# 2. Output of step N is input of step N+1 — explicit data flow
# 3. You can inject human review between steps — human in the loop
# 4. This is EXACTLY what LangChain LCEL pipelines do with the | operator
# 5. Each step can use a different model — cheap model for simple steps
# 6. Steps can run in parallel if they don't depend on each other (asyncio)
