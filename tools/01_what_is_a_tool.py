"""
╔══════════════════════════════════════════════════════════════╗
║  FILE 01 — What is a Tool?                                  ║
║  Concept : @tool decorator, schema, description             ║
║  Time    : 10 minutes                                       ║
╚══════════════════════════════════════════════════════════════╝

SESSION SCRIPT — READ THIS BEFORE RUNNING
==========================================

[SAY — Setting expectations]
"Before we write any code — let me ask you a question.

You built a contacts API in Days 2 and 3.
You built a chat API in the milestones.
But what if I asked your chatbot: 'How many contacts do I have?'

Try it mentally. Can it answer?

No. Because the LLM has no access to your database.
It can only work with what it was trained on.

THIS is the problem that LangChain Tools solve.

A tool is simply a Python function that the LLM can call.
You give it functions — it decides when to use them.
Without tools — the LLM is a brain with no hands.
With tools    — the LLM can actually DO things."

[SAY — Before coding]
"Let me show you the simplest possible tool first.
Then we'll build up to something impressive."

[DO — Open this file and run it section by section]

Run: python 01_what_is_a_tool.py
"""

import json
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()


# ══════════════════════════════════════════════════════════════
# SECTION 1 — The @tool decorator
# ══════════════════════════════════════════════════════════════

# [SAY]
# "The @tool decorator does three things:
#   1. Gives the function a name the LLM can reference
#   2. Reads the docstring as the description — LLM reads this
#      to decide WHEN to call this tool
#   3. Makes it compatible with LangChain's tool calling system
#
# The description is the most important part.
# Think of it as: instructions you're writing for the LLM
# so it knows when and how to use this tool."

@tool
def calculate(expression: str) -> str:
    """
    Evaluate a Python math expression and return the result.
    Use this when the user asks for any calculation or arithmetic.
    Pass only valid Python math: '2 + 2', '3500 * 15 / 100', '100 / 4'
    Do NOT use % symbol or words like 'of'. Use division instead.
    """
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}. Pass valid Python math like '3500 * 15 / 100'"


# ══════════════════════════════════════════════════════════════
# SECTION 2 — Inspect the tool schema
# ══════════════════════════════════════════════════════════════

# [SAY]
# "Let me show you what a tool looks like to the LLM.
#  This is the schema that gets sent to Groq or OpenAI.
#  The LLM reads this schema to understand:
#   - What is this tool called?
#   - What does it do?
#   - What parameters does it need?
#   - Which parameters are required?"

print("═" * 55)
print("What the tool looks like to the LLM:")
print("═" * 55)

print(f"\nName        : {calculate.name}")
print(f"Description : {calculate.description}")
print(f"\nFull schema (what gets sent to the model):")
print(json.dumps(calculate.args_schema.model_json_schema(), indent=2))

# [SAY]
# "Notice the 'required' field — it says expression is required.
#  Groq is strict about this — always make all params required.
#  No optional parameters with defaults in Groq tools."


# ══════════════════════════════════════════════════════════════
# SECTION 3 — Good vs Bad tool descriptions
# ══════════════════════════════════════════════════════════════

# [SAY]
# "The docstring is NOT just for humans — it's for the LLM.
#  A bad description = tool never gets called OR called wrong.
#  A good description = LLM uses it exactly when needed.
#
# Let me show you the difference."

print("\n" + "═" * 55)
print("Good vs Bad tool descriptions:")
print("═" * 55)

@tool
def bad_calculator(expression: str) -> str:
    """Calculate something."""  # ← vague, LLM won't know when to use this
    return eval(expression, {"__builtins__": {}})

@tool
def good_calculator(expression: str) -> str:
    """
    Evaluate a Python math expression and return the result.
    Use this when the user asks for any calculation or arithmetic.
    Pass only valid Python math: '2 + 2', '3500 * 15 / 100', '100 / 4'
    Do NOT use % symbol or words like 'of'. Use division instead.
    """
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"

print("\n BAD description:")
print(f"  '{bad_calculator.description}'")
print("  Problem: LLM doesn't know when to call this")
print("  Problem: LLM doesn't know what format to pass")

print("\n GOOD description:")
print(f"  '{good_calculator.description[:80]}...'")
print("  Clear: when to use it")
print("  Clear: what format to pass as expression")
print("  Clear: what NOT to do (no % symbol)")


# ══════════════════════════════════════════════════════════════
# SECTION 4 — Call the tool directly (no LLM yet)
# ══════════════════════════════════════════════════════════════

# [SAY]
# "Before we connect this to an LLM — let's call the tool directly.
#  This proves the function works on its own.
#  Always test tools independently before binding to LLM."

print("\n" + "═" * 55)
print("Calling the tool directly (no LLM):")
print("═" * 55)

tests = [
    {"expression": "2 + 2"},
    {"expression": "3500 * 15 / 100"},
    {"expression": "100 / 4"},
    {"expression": "invalid syntax!!"},
]

for test in tests:
    result = calculate.invoke(test)
    print(f"\n  Input  : {test}")
    print(f"  Output : {result}")


# ══════════════════════════════════════════════════════════════
# SECTION 5 — Groq-specific rules (important!)
# ══════════════════════════════════════════════════════════════

# [SAY]
# "Before we move to the next file — important rules for Groq.
#  Groq's tool calling is stricter than OpenAI.
#  If you break these rules you get a 400 error."

print("\n" + "═" * 55)
print("GROQ TOOL RULES — Remember these:")
print("═" * 55)
print("""
  1. No optional/default parameters
       def my_tool(param: str = "default")
       def my_tool(param: str)

  2. No int parameters — use str
       def get_contact(id: int)
       def get_contact(id: str)

  3. No tools with zero parameters — add dummy
       def list_all()
       def list_all(dummy: str)  # pass "execute"

  4. No forward slashes in string values
       timezone = "Asia/Kolkata"  → crashes Groq
       city     = "Kolkata"       → works fine

  5. Docstring examples matter — LLM copies them
       Examples: '15% of 500'    → LLM passes this literally
       Examples: '500 * 15 / 100' → LLM passes valid Python
""")

# [TRANSITION]
# "Now you understand what a tool is.
#  Next file — we connect it to the LLM and see it actually called."
