"""
Multi-Provider LLM Demo
========================
Demonstrates connecting to all major LLM providers.
Same code pattern — only client and model string changes.

API Keys — where to get them (all free tier available):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Provider      URL                              Free?
─────────────────────────────────────────────────────
Groq          console.groq.com                  Free
OpenAI        platform.openai.com/api-keys      Paid (cheap)
Anthropic     console.anthropic.com             Paid
Google Gemini aistudio.google.com               Free tier
OpenRouter    openrouter.ai/keys                Free credits
Ollama        ollama.ai (local — no key!)       Completely free

Install:
  pip install groq openai anthropic google-generativeai python-dotenv
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()


# ════════════════════════════════════════════════════
# UNIVERSAL RESPONSE PRINTER
# ════════════════════════════════════════════════════

def print_result(provider: str, model: str, response: str, elapsed: float, tokens: dict = None):
    print(f"\n{'═'*60}")
    print(f"  Provider : {provider}")
    print(f"  Model    : {model}")
    print(f"  Time     : {elapsed:.2f}s")
    if tokens:
        print(f"  Tokens   : {tokens.get('input',0)} in / {tokens.get('output',0)} out")
    print(f"{'─'*60}")
    print(f"  {response[:300]}")
    print(f"{'═'*60}")


# The same prompt sent to every provider
PROMPT = "Explain what an API is in exactly 2 sentences. Be concise."
SYSTEM = "You are a concise technical explainer. Never exceed the requested length."


# ════════════════════════════════════════════════════
# PROVIDER 1 — GROQ
# URL   : console.groq.com
# Free  :  Yes — generous free tier
# Speed :  Fastest (LPU chip)
# SDK   : pip install groq
# Models: llama-3.3-70b-versatile, mixtral-8x7b, gemma2-9b
# ════════════════════════════════════════════════════

def call_groq(prompt: str, system: str) -> dict:
    from groq import Groq

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    model  = "llama-3.3-70b-versatile"

    start    = time.time()
    response = client.chat.completions.create(
        model    = model,
        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ],
        temperature = 0.3,
        max_tokens  = 200,
    )
    elapsed = time.time() - start

    return {
        "provider": "Groq",
        "model"   : model,
        "response": response.choices[0].message.content,
        "elapsed" : elapsed,
        "tokens"  : {
            "input" : response.usage.prompt_tokens,
            "output": response.usage.completion_tokens,
        }
    }


# ════════════════════════════════════════════════════
# PROVIDER 2 — OPENAI
# URL   : platform.openai.com/api-keys
# Free  :  Paid — $5 free credit on signup
# Speed :  Fast
# SDK   : pip install openai
# Models: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
# ════════════════════════════════════════════════════

def call_openai(prompt: str, system: str) -> dict:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model  = "gpt-4o-mini"   # cheapest OpenAI model — good for demos

    start    = time.time()
    response = client.chat.completions.create(
        model    = model,
        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ],
        temperature = 0.3,
        max_tokens  = 200,
    )
    elapsed = time.time() - start

    return {
        "provider": "OpenAI",
        "model"   : model,
        "response": response.choices[0].message.content,
        "elapsed" : elapsed,
        "tokens"  : {
            "input" : response.usage.prompt_tokens,
            "output": response.usage.completion_tokens,
        }
    }


# ════════════════════════════════════════════════════
# PROVIDER 3 — ANTHROPIC (CLAUDE)
# URL   : console.anthropic.com
# Free  :  Paid — $5 free credit on signup
# Speed :  Medium
# SDK   : pip install anthropic
# Models: claude-3-5-sonnet, claude-3-haiku, claude-3-opus
# NOTE  : Different SDK — no messages[0] system role
#         System prompt is a separate parameter
# ════════════════════════════════════════════════════

def call_anthropic(prompt: str, system: str) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    model  = "claude-3-haiku-20240307"   # fastest + cheapest Claude

    start    = time.time()
    response = client.messages.create(
        model      = model,
        max_tokens = 200,
        system     = system,    # ← Anthropic: system is separate param, NOT in messages[]
        messages   = [
            {"role": "user", "content": prompt}   # no system role here
        ],
    )
    elapsed = time.time() - start

    return {
        "provider": "Anthropic (Claude)",
        "model"   : model,
        "response": response.content[0].text,     # ← different response structure
        "elapsed" : elapsed,
        "tokens"  : {
            "input" : response.usage.input_tokens,
            "output": response.usage.output_tokens,
        }
    }


# ════════════════════════════════════════════════════
# PROVIDER 4 — GOOGLE GEMINI
# URL   : aistudio.google.com → Get API Key
# Free  :  Free tier (60 req/min on Flash)
# Speed :  Fast (Flash model)
# SDK   : pip install google-generativeai
# Models: gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash
# NOTE  : Completely different SDK structure
# ════════════════════════════════════════════════════

def call_gemini(prompt: str, system: str) -> dict:
    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    model_name = "gemini-1.5-flash"

    model = genai.GenerativeModel(
        model_name        = model_name,
        system_instruction= system,   # ← Gemini: system as constructor param
    )

    start    = time.time()
    response = model.generate_content(
        prompt,
        generation_config = genai.GenerationConfig(
            temperature    = 0.3,
            max_output_tokens = 200,
        )
    )
    elapsed = time.time() - start

    return {
        "provider": "Google Gemini",
        "model"   : model_name,
        "response": response.text,
        "elapsed" : elapsed,
        "tokens"  : {
            "input" : response.usage_metadata.prompt_token_count,
            "output": response.usage_metadata.candidates_token_count,
        }
    }


# ════════════════════════════════════════════════════
# PROVIDER 5 — OPENROUTER
# URL   : openrouter.ai/keys
# Free  :  Free credits on signup
# Speed : Depends on model chosen
# SDK   : pip install openai (uses OpenAI SDK!)
# Models: ALL models from ALL providers via one key
# KEY POINT: Same OpenAI SDK — just change base_url
# ════════════════════════════════════════════════════

def call_openrouter(prompt: str, system: str, model: str = "openai/gpt-4o-mini") -> dict:
    from openai import OpenAI

    # Same OpenAI client — different base_url
    client = OpenAI(
        api_key  = os.getenv("OPENROUTER_API_KEY"),
        base_url = "https://openrouter.ai/api/v1",
    )

    start    = time.time()
    response = client.chat.completions.create(
        model    = model,   # ← just change this string to switch providers
        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ],
        temperature = 0.3,
        max_tokens  = 200,
    )
    elapsed = time.time() - start

    return {
        "provider": f"OpenRouter → {model}",
        "model"   : model,
        "response": response.choices[0].message.content,
        "elapsed" : elapsed,
        "tokens"  : {
            "input" : response.usage.prompt_tokens,
            "output": response.usage.completion_tokens,
        }
    }


# ════════════════════════════════════════════════════
# PROVIDER 6 — OLLAMA (LOCAL)
# URL   : ollama.ai → Download and install
# Free  :  100% free — runs on your machine
# Speed : Depends on your hardware
# SDK   : pip install openai (uses OpenAI SDK!)
# Models: llama3.2, mistral, phi3, gemma2, codellama
# Setup : ollama pull llama3.2 (in terminal first)
# NOTE  : No internet needed — fully offline
# ════════════════════════════════════════════════════

def call_ollama(prompt: str, system: str, model: str = "llama3.2") -> dict:
    from openai import OpenAI

    # No API key needed for local Ollama
    client = OpenAI(
        api_key  = "ollama",                      # any string works
        base_url = "http://localhost:11434/v1",   # local server
    )

    start = time.time()
    try:
        response = client.chat.completions.create(
            model    = model,
            messages = [
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            temperature = 0.3,
            max_tokens  = 200,
        )
        elapsed = time.time() - start

        return {
            "provider": "Ollama (Local)",
            "model"   : model,
            "response": response.choices[0].message.content,
            "elapsed" : elapsed,
            "tokens"  : {
                "input" : response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
            }
        }
    except Exception as e:
        return {
            "provider": "Ollama (Local)",
            "model"   : model,
            "response": f" Error: {e}\nMake sure Ollama is running: ollama serve",
            "elapsed" : 0,
            "tokens"  : {}
        }


# ════════════════════════════════════════════════════
# UNIVERSAL WRAPPER
# One function to rule them all
# Shows how to build provider-agnostic code
# ════════════════════════════════════════════════════

def call_llm(provider: str, prompt: str, system: str, **kwargs) -> dict:
    """
    Universal LLM caller.
    Switch provider by changing one string.
    """
    providers = {
        "groq"       : call_groq,
        "openai"     : call_openai,
        "anthropic"  : call_anthropic,
        "gemini"     : call_gemini,
        "openrouter" : call_openrouter,
        "ollama"     : call_ollama,
    }

    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}. Choose from: {list(providers.keys())}")

    return providers[provider](prompt, system, **kwargs)


# ════════════════════════════════════════════════════
# RUN ALL PROVIDERS
# Comment out providers you don't have keys for
# ════════════════════════════════════════════════════

if __name__ == "__main__":

    print("\n Calling all LLM providers with the same prompt...")
    print(f" Prompt: {PROMPT}\n")

    # ── Track all results for comparison ──────────────
    results = []

    # ── Groq ──────────────────────────────────────────
    if os.getenv("GROQ_API_KEY"):
        try:
            r = call_groq(PROMPT, SYSTEM)
            print_result(**r)
            results.append(r)
        except Exception as e:
            print(f" Groq failed: {e}")

    # ── OpenAI ────────────────────────────────────────
    if os.getenv("OPENAI_API_KEY"):
        try:
            r = call_openai(PROMPT, SYSTEM)
            print_result(**r)
            results.append(r)
        except Exception as e:
            print(f" OpenAI failed: {e}")

    # ── Anthropic ─────────────────────────────────────
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            r = call_anthropic(PROMPT, SYSTEM)
            print_result(**r)
            results.append(r)
        except Exception as e:
            print(f" Anthropic failed: {e}")

    # ── Google Gemini ─────────────────────────────────
    if os.getenv("GOOGLE_API_KEY"):
        try:
            r = call_gemini(PROMPT, SYSTEM)
            print_result(**r)
            results.append(r)
        except Exception as e:
            print(f" Gemini failed: {e}")

    # ── OpenRouter — try multiple models with one key ─
    if os.getenv("OPENROUTER_API_KEY"):
        or_models = [
            "openai/gpt-4o-mini",
            "anthropic/claude-3-haiku",
            "google/gemini-flash-1.5",
            "meta-llama/llama-3.3-70b-instruct",
            "mistralai/mistral-7b-instruct",
        ]
        for model in or_models:
            try:
                r = call_openrouter(PROMPT, SYSTEM, model=model)
                print_result(**r)
                results.append(r)
            except Exception as e:
                print(f" OpenRouter/{model} failed: {e}")

    # ── Ollama — local models ─────────────────────────
    ollama_models = ["llama3.2", "mistral", "phi3"]
    for model in ollama_models:
        r = call_ollama(PROMPT, SYSTEM, model=model)
        print_result(**r)
        if "Error" not in r["response"]:
            results.append(r)
        break   # try first available model only


    # ════════════════════════════════════════════════
    # COMPARISON TABLE
    # ════════════════════════════════════════════════
    if results:
        print("\n" + "═" * 70)
        print(" COMPARISON TABLE")
        print("═" * 70)
        print(f"  {'Provider':<30} {'Model':<25} {'Time':>6}  {'Tokens':>8}")
        print("─" * 70)
        for r in sorted(results, key=lambda x: x["elapsed"]):
            tok = r.get("tokens", {})
            token_str = f"{tok.get('input',0)}+{tok.get('output',0)}"
            print(f"  {r['provider']:<30} {r['model']:<25} {r['elapsed']:>5.2f}s  {token_str:>8}")
        print("═" * 70)

        fastest = min(results, key=lambda x: x["elapsed"])
        print(f"\n   Fastest : {fastest['provider']} ({fastest['elapsed']:.2f}s)")


    # ════════════════════════════════════════════════
    # KEY INSIGHT FOR LEARNERS
    # ════════════════════════════════════════════════
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY TAKEAWAYS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. SAME MESSAGE ARRAY everywhere
   system + user + assistant — universal across all providers

2. DIFFERENT SDKs — but same concept
   Groq    → from groq import Groq
   OpenAI  → from openai import OpenAI
   Claude  → import anthropic (system is a separate param!)
   Gemini  → import google.generativeai (completely different!)
   Ollama  → from openai import OpenAI (reuses OpenAI SDK!)

3. OpenRouter = one key for everything
   Change model string → different provider
   Perfect for: comparing models, fallback logic, cost optimisation

4. Ollama = no key, no cost, no internet
   Perfect for: privacy, offline use, development

5. In production — abstract the provider
   Build call_llm(provider, prompt) → swap without changing app code
   LangChain does this for you → Module 9
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
