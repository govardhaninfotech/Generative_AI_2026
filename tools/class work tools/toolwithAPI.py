from langchain.tools import tool
import requests


@tool
def renderData(id: int):
    """render data from api"""

    url = f"https://jsonplaceholder.typicode.com/todos/{id}"
    
    responce = requests.get(url)
    
    return responce.json()

print(renderData.invoke({"id":100}))
