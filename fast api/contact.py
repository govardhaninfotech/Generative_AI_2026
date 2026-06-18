from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

user = [
    {
        "name":"Kunj",
        "email":"kunj@gmail.com",
        "phone":1234567890
    },
    {
        "name":"Krishna",
        "email":"Krishna@gmail.com",
        "phone":9876543210
    }
]

@app.get("/")
def welcome():
    return {"message":"welcome to fastapi "}

@app.get('/search')
def search(name:str="",phone:int=0):
    for i in user:
        if i["name"] == name or i["phone"] == phone:
            return {"data":i}
    return{"message":f"welcome {name}"}