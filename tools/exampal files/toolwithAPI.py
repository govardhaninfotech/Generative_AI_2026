import requests
from langchain.tools import tool

@tool
def getData(id : int):
    '''fetch data from API'''

    url=f"https://jsonplaceholder.typicode.com/posts/{id}"
    
    responce = requests.get(url)
    
    return responce.json() 

print(getData.invoke({"id":1}))