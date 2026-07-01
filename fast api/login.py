from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

users= []

class RegisterUser(BaseModel):
    name : str
    email : str
    phone : int
    password : str
    c_password : str

class LoginUser(BaseModel):
    email : str
    password : str
    

@app.get("/")
def display():
    return {"message":"welcome to gi "}
# display all users
@app.get("/users/{start_id}&{end_id}")
def display_users(start_id:int=0,end_id:int=len(users)):
    temp = []
    for i in users:
        if i.id>=start_id and i.id<=end_id:
            temp.append(i)
    return {"users":temp}

# register user
@app.post("/register")
def register(user :RegisterUser ):
    users.append(user)
    print(users)
    return {"message":"registerd..!"}
    
    

# login user
@app.post("/login")
def login(user : LoginUser):
    for i in users:
        if i.email == user.email:
            if i.password == user.password:
                return{"message":f"{i.name} is login...😮😁😒👀"} 
    
    return{"error":"id and password does not match..!"}