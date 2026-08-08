from langchain.tools import tool


@tool
def add(a: int, b: int) -> int:
    """For do sum of 2 number"""
    return a + b

print(add.invoke({"a":10,"b":90}))
