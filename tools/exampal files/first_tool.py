from langchain.tools import tool

@tool
def hello(name:str) -> str:
    """say hello to someone"""
    return f"hello {name}"

print(hello.invoke("raj"))