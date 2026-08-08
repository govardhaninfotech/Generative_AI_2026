import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, max_retries=3)

@tool
def calculate(expression: str) -> str:
    """
    Evaluate a Python math expression and return the result.
    Use when the user asks for any calculation or arithmetic.
    Pass valid Python math only: '2 + 2', '3500 * 15 / 100', '100 / 4'
    Do NOT use % or words like 'of'. Use division for percentages.
    """
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}. Pass valid Python math like '3500 * 15 / 100'"


@tool
def convert_currency(amount: str, from_currency: str, to_currency: str) -> str:
    """
    Convert money from one currency to another.
    Use when the user asks to convert between currencies.
    amount: the number as a string like '500'.
    from_currency and to_currency: use codes like USD, INR, EUR, GBP, AED.
    """
    try:
        amt = float(amount)
    except ValueError:
        return f"Invalid amount: {amount}"

    rates = {
        "USD_INR": 84.5,  "INR_USD": 0.012,
        "EUR_USD": 1.08,  "USD_EUR": 0.92,
        "GBP_USD": 1.27,  "USD_GBP": 0.79,
        "USD_AED": 3.67,  "AED_USD": 0.27,
        "EUR_INR": 91.3,  "INR_EUR": 0.011,
        "GBP_INR": 107.2, "INR_GBP": 0.009,
    }

    pair = f"{from_currency.upper()}_{to_currency.upper()}"
    if pair in rates:
        result = amt * rates[pair]
        return f"{amount} {from_currency.upper()} = {result:.2f} {to_currency.upper()}"
    return f"Rate for {from_currency} to {to_currency} not available. Supported: USD, INR, EUR, GBP, AED"


@tool
def search_contacts(name_query: str) -> str:
    """
    Search for contacts by name in the contacts database.
    Use when user wants to find, look up, or search for a contact by name.
    Pass the name or partial name to search for.
    Requires contacts API running at http://localhost:8000.
    """
    import requests
    API_KEY = os.getenv("CONTACTS_API_KEY", "admin-secret-change-in-production")
    try:
        r = requests.get(
            "http://localhost:8000/contacts",
            headers={"X-API-Key": API_KEY},
            timeout=5,
        )
        if r.status_code == 200:
            contacts = r.json()
            matches  = [
                c for c in contacts
                if name_query.lower() in c["name"].lower()
            ]
            if not matches:
                return f"No contacts found matching '{name_query}'"
            lines = [f"Found {len(matches)} match(es) for '{name_query}':"]
            for c in matches:
                lines.append(f"  ID:{c['id']} | {c['name']} | {c['phone']}")
            return "\n".join(lines)
        return f"Error {r.status_code}"
    except requests.ConnectionError:
        return "Contacts API not reachable. Run: uvicorn solution:app --reload"


# SECTION 1 — Bind all tools


all_tools = [calculate, convert_currency, search_contacts]
llm_tools = llm.bind_tools(all_tools)
tool_map  = {t.name: t for t in all_tools}

print("═" * 55)
print("Tools bound to LLM:")
for t in all_tools:
    print(f"  • {t.name}")
print("═" * 55)


# SECTION 2 — LLM picks the right tool

def ask(question: str) -> str:
    """Clean tool calling loop."""
    print(f"\n{'─'*50}")
    print(f" {question}")

    messages = [HumanMessage(content=question)]
    response = llm_tools.invoke(messages)
    messages.append(response)

    if not response.tool_calls:
        print(f"   (direct — no tool needed): {response.content}")
        return response.content
    print(response.tool_calls)
    for tc in response.tool_calls:
        print(f"   Tool selected : {tc['name']}")
        print(f"     Args         : {tc['args']}")
        try:
            result = tool_map[tc["name"]].invoke(tc["args"])
        except Exception as e:
            result = f"Error: {e}"
        print(f"     Result       : {result}")
        messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

    final = llm_tools.invoke(messages)
    print(f"   Answer: {final.content}")
    return final.content


print("\nSECTION 2 — LLM picks the right tool:\n")

# ask("What is 840 multiplied by 25?")                     # → calculate
# ask("How much is 500 USD in Indian Rupees?")              # → convert_currency
# ask("Find contacts with the name Priya")                  # → search_contacts
# ask("What is the capital of France?")                     # → no tool (direct)
# ask("If I earn 75000 per month what is my annual salary?")# → calculate
# ask("Convert 1000 EUR to INR")                            # → convert_currency
ask("Convert 1000 USD to INR and then calculate 18% GST on that amount")


print("\n" + "═" * 55)
print("SECTION 3 — Multi-step tool use:")
print("═" * 55)

ask("Convert 1000 USD to INR and then calculate 18% GST on that amount")


print("\n" + "═" * 55)
print("TOOL DESIGN PRINCIPLE:")
print("═" * 55)
print("""
  Only create a tool for what the LLM genuinely CANNOT do:

   Need a tool        Don't need a tool
  ─────────────────    ────────────────────────
  Database access      Timezone conversions
  Live API calls       Simple math facts
  File read/write      Capital city lookups
  Send email/SMS       Unit conversions (simple)
  Web scraping         Language translations

  Rule: if the LLM can answer it from training data → no tool needed.
        if it requires live data or system access   → tool needed.
""")

