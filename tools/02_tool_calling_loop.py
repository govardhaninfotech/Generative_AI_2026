import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()


llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, max_retries=3)


# ── Tool definition ───────────────────────────────────────────────
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
        return f"Error: {e}"


# ══════════════════════════════════════════════════════════════
# SECTION 1 — bind_tools
# ══════════════════════════════════════════════════════════════

llm_with_tools = llm.bind_tools([calculate])
"""
print("═" * 55)
print("SECTION 1 — bind_tools")
print("═" * 55)
print(f"Tools bound: {[calculate.name]}")
print("LLM now knows about the 'calculate' tool")
"""

# ══════════════════════════════════════════════════════════════
# SECTION 2 — First call — LLM requests the tool
# ══════════════════════════════════════════════════════════════


print("\n" + "═" * 55)
print("SECTION 2 — LLM requests the tool (step 1-2)")
print("═" * 55)

question = "What is 15% of 3500?"
# question = "What is the capital   of india"
messages = [HumanMessage(content=question)]

print(f"\n Question: {question}")
print("\nSending to LLM...")

response = llm_with_tools.invoke(messages)

'''
print(f"\nresponse.content    : '{response.content}'")
print(f"response.tool_calls : {response.tool_calls}")

dic = {"calculate": calculate}

if response.tool_calls:
    tc = response.tool_calls[0]
    # print(tc["name"](tc["args"]))
    print("+"*50)
    # print(dic[tc["name"]])
    # print(type(dic[tc["name"]]))
    # print(type(tc["name"]), type((tc["args"])))
    print(f"\nTool requested : {tc['name']}")
    print(f"Arguments      : {tc['args']}")
    print(f"Tool call ID   : {tc['id']}")


# ══════════════════════════════════════════════════════════════
# SECTION 3 — Run the tool + send result back
# ══════════════════════════════════════════════════════════════

print("\n" + "═" * 55)
print("SECTION 3 — Run tool + ToolMessage (step 3-5)")
print("═" * 55)

messages.append(response)   # add LLM response to history

if response.tool_calls:
    tc          = response.tool_calls[0]
    tool_result = calculate.invoke(tc["args"])   # run the tool

    print(f"\n Running: {tc['name']}({tc['args']})")
    print(f"   Result : {tool_result}")

    # Send result back as ToolMessage
    messages.append(ToolMessage(
        content      = str(tool_result),
        tool_call_id = tc["id"],        # must match the request
    ))
    print(f"\nToolMessage added to messages")
    print(f"Messages so far: {len(messages)} messages in chain")

'''

print("\n" + "═" * 55)
print("SECTION 4 — Final answer (step 6)")
print("═" * 55)

final = llm_with_tools.invoke(messages)
print(f"\n Final answer: {final.content}")


print("\n" + "═" * 55)
print("SECTION 5 — Full loop as a reusable function")
print("═" * 55)

tool_map = {calculate.name: calculate}

def ask_with_tools(question: str) -> str:
    """The tool calling loop — complete and reusable."""
    print(f"\n {question}")

    messages = [HumanMessage(content=question)]

    # Step 1-2: First LLM call
    response = llm_with_tools.invoke(messages)
    messages.append(response)

    # Step 3-5: If tool requested — run it and return result
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"   Tool called : {tc['name']}({tc['args']})")
            result = tool_map[tc["name"]].invoke(tc["args"])
            print(f"   Tool result : {result}")
            messages.append(ToolMessage(
                content      = str(result),
                tool_call_id = tc["id"],
            ))

        # Step 6: Final LLM call with tool result
        final = llm_with_tools.invoke(messages)
        print(f"   Answer      : {final.content}")
        return final.content
    else:
        # LLM answered directly — no tool needed
        print(f"   Direct answer: {response.content}")
        return response.content


# Test — LLM decides when to use the tool
ask_with_tools("What is 25 multiplied by 840?")
ask_with_tools("What is the capital of France?")    # no tool needed
ask_with_tools("If I have 12500 and spend 3200, how much is left?")


'''


print("\n" + "═" * 55)
print("KEY TAKEAWAYS:")
print("═" * 55)
print("""
  1. bind_tools → tells LLM about available tools
  2. response.tool_calls → LLM's REQUEST to call a tool
  3. YOU run the tool — LLM cannot run it itself
  4. ToolMessage → how you send the result back
  5. LLM decides when to use a tool — you don't hardcode it
  6. tool_call_id → links result to the request (required!)

  The loop:
  Question → LLM → tool_calls? → run tool → ToolMessage → LLM → Answer
""")

# [TRANSITION]
# "You now understand the tool calling loop completely.
#  Next file — what if we have MULTIPLE tools?
#  How does the LLM decide which one to use?"

'''