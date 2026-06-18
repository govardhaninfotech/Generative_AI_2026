from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def display():
    return {"message": "Welcome to govardhan"}


@app.get("/user")
def display():
    return {"user": {"email": "user1@gamil.com", "password": "user@123"}}
