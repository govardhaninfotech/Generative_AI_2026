from fastapi import FastAPI

from models import ChatRequest, ChatResponse

from llm import ask_llm

app = FastAPI()


@app.get("/")
def home():

    return {"message": "Backend Running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    answer = ask_llm(request.message)

    return ChatResponse(answer=answer)
