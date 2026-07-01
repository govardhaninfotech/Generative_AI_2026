from fastapi import FastAPI
from pydantic import BaseModel
from validation import email_validation
from database import get_data

app = FastAPI()

user = get_data()

class RegisterUser(BaseModel):
    name: str
    email: str
    phone: int


@app.get("/")
def welcome():
    return {"users":user}


@app.get("/search")
def search(name: str = "", phone: int = 0):
    for i in user:
        if i["name"] == name or i["phone"] == phone:
            return {"data": i}
    return {"message": f"welcome {name}"}


@app.get("/users/{start_id}&{end_id}")
def display_users(start_id:int=0,end_id:int=len(user)):
    temp = []
    for i in user:
        if i["id"]>=start_id and i["id"]<=end_id:
            temp.append(i)
    return {"users":temp}

# @app.get("/users")
# def displayallUsers():
#     return {"message": user}


@app.put("/update")
def update(upd_user : RegisterUser,email: str = "", phone: int = 0):
    email = email_validation(email)
    if email:
        index = 0
        for i in user:
            if i["email"] == email or i["phone"] == phone:
                user[index] = upd_user
                return {"message":"vontact update...!","data":upd_user}
            index +=1
    else:
        return{"message":"email is not valid"}
    return {"message": "not contact found..!"}
