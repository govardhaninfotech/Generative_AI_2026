from dotenv import load_dotenv

from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile")


def ask_llm(question: str):

    response = llm.invoke(question)

    return response.content
