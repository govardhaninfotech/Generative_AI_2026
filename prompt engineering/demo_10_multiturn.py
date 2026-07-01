"""
Demo 10 — Multi-turn Conversation
PE Concept : Managing message history — the model has no memory by default
Scenario   : Developer assistant that remembers context across turns
             Build the foundation of every chatbot and AI agent

Key insight: There is no magic memory. YOU manage the history array.
             LangChain's memory, agents' state — all just messages arrays.
             Understanding this = understanding everything that follows.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"


# ════════════════════════════════════════════════════
# PART A — Prove the model has no memory
# ════════════════════════════════════════════════════

print("═" * 60)
print("PART A — Proving the model has NO memory")
print("═" * 60)

def stateless_ask(message: str) -> str:
    """Every call is completely independent — no history."""
    response = client.chat.completions.create(
        model    = MODEL,
        messages = [{"role": "user", "content": message}]
    )
    return response.choices[0].message.content

print(stateless_ask("My name is Raj and I'm building a FastAPI contacts app."))
print("\nAsking again in new call:")
print(stateless_ask("What is my name and what am I building?"))
# The model won't remember — clean proof of statelessness


# ════════════════════════════════════════════════════
# PART B — Simple conversation manager
# Most important class of this session
# ════════════════════════════════════════════════════

class ConversationManager:
    """
    The simplest possible chatbot.
    All it does: maintain the messages array.
    This is what LangChain's ConversationBufferMemory does under the hood.
    """

    def __init__(self, system_prompt: str):
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]
        self.turn_count = 0

    def chat(self, user_message: str) -> str:
        # Add user message to history
        self.messages.append({"role": "user", "content": user_message})

        # Send full history to LLM
        response = client.chat.completions.create(
            model    = MODEL,
            messages = self.messages,
            temperature = 0.5
        )
        assistant_reply = response.choices[0].message.content

        # Add assistant reply to history (critical — model needs this for context)
        self.messages.append({"role": "assistant", "content": assistant_reply})

        self.turn_count += 1
        return assistant_reply

    def get_history(self) -> list:
        return [m for m in self.messages if m["role"] != "system"]

    def token_estimate(self) -> int:
        """Rough estimate: 4 chars ≈ 1 token."""
        total_chars = sum(len(m["content"]) for m in self.messages)
        return total_chars // 4

    def reset(self):
        system = self.messages[0]
        self.messages = [system]
        self.turn_count = 0


# ── Test conversation memory ───────────────────────────────────
DEV_ASSISTANT_SYSTEM = """
You are an expert FastAPI and Python developer assistant.
You remember everything discussed in this conversation.
Be concise but thorough. Use code examples when helpful.
"""

bot = ConversationManager(DEV_ASSISTANT_SYSTEM)

print("\n" + "═" * 60)
print("PART B — Conversation with memory")
print("═" * 60)

conversation = [
    "I'm building an API for a hospital. I need to store patient records.",
    "What database would you recommend for this use case and why?",
    "Good point. How would I set that up with FastAPI and the DI pattern we discussed?",
    "What are the top 3 security concerns I should handle for this specific use case?",
    "Summarise everything we've discussed so far in bullet points.",
]

for turn, user_msg in enumerate(conversation, 1):
    print(f"\n Turn {turn}: {user_msg}")
    reply = bot.chat(user_msg)
    print(f" {reply[:300]}")
    print(f"   [History: {len(bot.get_history())} messages | ~{bot.token_estimate()} tokens used]")


# ════════════════════════════════════════════════════
# PART C — Context window management
# What happens when history gets too long?
# ════════════════════════════════════════════════════

class SmartConversationManager(ConversationManager):
    """
    Production-ready conversation manager.
    Handles context window limits intelligently.
    """

    def __init__(self, system_prompt: str, max_tokens: int = 4000):
        super().__init__(system_prompt)
        self.max_tokens = max_tokens

    def _trim_history(self):
        """
        When approaching token limit:
        Keep system prompt + last N exchanges.
        Summarise older messages.
        """
        if self.token_estimate() < self.max_tokens * 0.8:
            return  # still safe, no trimming needed

        print(f"     Context limit approaching ({self.token_estimate()} tokens) — trimming...")

        # Keep system prompt + last 4 messages (2 exchanges)
        system = self.messages[0]
        recent = self.messages[-4:]

        # Summarise what was dropped
        dropped = self.messages[1:-4]
        if dropped:
            summary_text = "\n".join(m["content"][:100] for m in dropped)
            summary_msg = {
                "role"   : "system",
                "content": f"[Earlier conversation summary]: {summary_text[:500]}..."
            }
            self.messages = [system, summary_msg] + recent
        else:
            self.messages = [system] + recent

    def chat(self, user_message: str) -> str:
        self._trim_history()
        return super().chat(user_message)


# ════════════════════════════════════════════════════
# PART D — Different memory strategies
# Show the trade-offs — connect to LangChain memory types
# ════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("PART D — Memory Strategies")
print("═" * 60)

strategies = {
    "Buffer Memory": """
        Store all messages forever.
         Perfect recall
         Context window fills up
         Cost grows with conversation length
        → LangChain: ConversationBufferMemory
    """,
    "Window Memory": """
        Keep only last N exchanges.
         Bounded cost and tokens
         Loses old context
        → LangChain: ConversationBufferWindowMemory(k=5)
    """,
    "Summary Memory": """
        Summarise old exchanges, keep recent ones in full.
         Bounded tokens, some long-term context
         Summarisation loses detail
        → LangChain: ConversationSummaryMemory
    """,
    "Entity Memory": """
        Extract and track entities (people, projects, dates) separately.
         Efficient, targeted recall
         Complex to implement
        → LangChain: ConversationEntityMemory
    """,
    "Vector Memory": """
        Embed all messages, retrieve semantically relevant ones.
         Scalable, relevant recall
         Requires vector DB, slower
        → Used in RAG-based memory (Module 14)
    """
}

for strategy, description in strategies.items():
    print(f"\n {strategy}:{description}")


print("\n" + "═" * 60)
print(" Summary: The messages array IS memory.")
print("   Everything else (LangChain, agents, RAG) is just a smarter way to manage it.")
print("═" * 60)


# ── Teaching points ───────────────────────────────
# 1. Model has ZERO memory — stateless API — this is a feature not a bug
# 2. YOU own the history — this is power, not a limitation
# 3. Every LangChain memory type = different strategy for managing messages[]
# 4. Token count grows with history — always monitor it
# 5. System prompt counts toward tokens every turn — keep it tight
# 6. Next module: LangChain handles all this with one line of config
