import os, requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()

llm      = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, max_retries=3)
API_BASE = "http://localhost:8000"
API_KEY  = os.getenv("CONTACTS_API_KEY", "admin-secret-change-in-production")
HEADERS  = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


# SECTION 1 — Wrap API endpoints as tools

@tool
def check_api_health(dummy: str) -> str:
    """
    Check if the Contacts API is running and healthy.
    Use when user asks about API status, health, or if it's working.
    Pass 'execute' as dummy parameter.
    """
    try:
        r = requests.get(f"{API_BASE}/health", headers=HEADERS, timeout=5)
        if r.status_code == 200:
            d = r.json()
            return (f"API is {d.get('status')} | "
                    f"Database: {d.get('database')} | "
                    f"Total chats: {d.get('total_chats', 0)}")
        return f"API returned status {r.status_code}"
    except requests.ConnectionError:
        return " Cannot connect. Start API: uvicorn solution:app --reload"


@tool
def get_all_contacts(dummy: str) -> str:
    """
    Retrieve and list all contacts from the database.
    Use when user wants to see, list, show, or count contacts.
    Pass 'execute' as dummy parameter.
    """
    try:
        r = requests.get(f"{API_BASE}/contacts", headers=HEADERS, timeout=5)
        if r.status_code == 200:
            contacts = r.json()
            if not contacts:
                return "No contacts in the database."
            lines = [f"Found {len(contacts)} contact(s):"]
            for c in contacts:
                lines.append(f"  ID:{c['id']} | {c['name']} | {c['phone']}")
            return "\n".join(lines)
        return f"Error {r.status_code}: {r.text}"
    except requests.ConnectionError:
        return "Cannot connect to API."


@tool
def get_contact_by_id(contact_id: str) -> str:
    """
    Get details of a specific contact by their ID number.
    Use when user asks for a specific contact by ID.
    Pass the ID as a string.
    """
    try:
        r = requests.get(f"{API_BASE}/contacts/{contact_id}",
                        headers=HEADERS, timeout=5)
        if r.status_code == 200:
            c = r.json()
            return f"Contact: ID={c['id']} | Name={c['name']} | Phone={c['phone']}"
        elif r.status_code == 404:
            return f"Contact with ID {contact_id} not found."
        return f"Error {r.status_code}"
    except requests.ConnectionError:
        return "Cannot connect to API."


@tool
def create_contact(name: str, phone: str) -> str:
    """
    Add a new contact to the database.
    Use when user wants to add, save, or create a new contact.
    name: full name as a string.
    phone: exactly 10 digits, no spaces, no dashes.
    """
    try:
        r = requests.post(
            f"{API_BASE}/contacts",
            headers = HEADERS,
            json    = {"name": name, "phone": phone},
            timeout = 5,
        )
        if r.status_code == 201:
            c = r.json()
            return f" Created: {c['name']} (ID:{c['id']}, Phone:{c['phone']})"
        elif r.status_code == 409:
            return f"Phone {phone} already exists in contacts."
        elif r.status_code == 422:
            return f"Validation error: {r.json()}"
        return f"Error {r.status_code}: {r.text}"
    except requests.ConnectionError:
        return "Cannot connect to API."


@tool
def delete_contact(contact_id: str) -> str:
    """
    Delete a contact from the database by their ID.
    Use when user wants to remove, delete, or clear a specific contact.
    Pass the contact ID as a string.
    """
    try:
        r = requests.delete(
            f"{API_BASE}/contacts/{contact_id}",
            headers = HEADERS,
            timeout = 5,
        )
        if r.status_code == 204:
            return f" Contact {contact_id} deleted successfully."
        elif r.status_code == 404:
            return f"Contact {contact_id} not found."
        return f"Error {r.status_code}"
    except requests.ConnectionError:
        return "Cannot connect to API."



# SECTION 2 — Bind and create the agent loop

contacts_tools   = [check_api_health, get_all_contacts, get_contact_by_id,
                    create_contact, delete_contact]
llm_contacts     = llm.bind_tools(contacts_tools)
tool_map         = {t.name: t for t in contacts_tools}


def contacts_agent(user_message: str) -> str:
    """Natural language interface to the Contacts API."""
    print(f"\n{'═'*55}")
    print(f" {user_message}")

    messages = [
        HumanMessage(content=f"""
You are a contacts management assistant.
You have tools to manage a contacts database.
For tools that need a dummy parameter — pass "execute".
Always use the most appropriate tool.

User request: {user_message}
        """)
    ]

    # Agent loop — LLM may call multiple tools in sequence
    for iteration in range(5):
        response = llm_contacts.invoke(messages)
        messages.append(response)

        # No tool calls — LLM gave the final answer
        if not response.tool_calls:
            print(f" {response.content}")
            return response.content

        # Process each tool call
        for tc in response.tool_calls:
            print(f"   [{iteration+1}] {tc['name']}({list(tc['args'].values())[:1]})")
            try:
                result = tool_map[tc["name"]].invoke(tc["args"])
            except Exception as e:
                result = f"Tool error: {e}"
            print(f"     → {result}")
            messages.append(ToolMessage(
                content      = str(result),
                tool_call_id = tc["id"],
            ))

    return "Max iterations reached"



# SECTION 3 — THE WOW MOMENT

print("\n" + "═" * 55)
print("SECTION 3 — Natural language → real API calls")
print("═" * 55)


contacts_agent("Is the API working?")

contacts_agent("Show me all my contacts")

contacts_agent("Add Priya Shah with phone number 9988776655")
contacts_agent("Create a contact for Raj Patel, number 8877665544")

contacts_agent("How many contacts do I have now?")

contacts_agent("Show me the details of contact number 1")

contacts_agent("Delete the contact with ID 1")

contacts_agent("List all contacts again")



# SECTION 4 — What just happened

print("\n" + "═" * 55)
print("WHAT JUST HAPPENED:")
print("═" * 55)
print("""
  Plain English → LLM → tool_calls → real API → response → answer

  Your FastAPI code: UNCHANGED
  Your database    : CHANGED (real inserts, deletes)
  The magic        : @tool + bind_tools + the loop

  This is how:
    ChatGPT plugins work
    Siri actions work
    Google Assistant integrations work
    Every AI agent with real-world access works

  Next: combine tools + documents + tracing → full agent
""")
