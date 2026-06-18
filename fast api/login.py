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
@app.get("/Users")
def display_users():
    return {"users":users}

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