from langchain.tools import tool

'''

@tool
def welcome(name:str)->str:
    """hello message"""
    return f"hello {name}"

print(welcome.invoke("Raj"))
'''


@tool
def add(a: int, b: int) -> int:
    """ sum of 2 number"""
    return a + b

print(add.invoke({"a":10,"b":20}))
