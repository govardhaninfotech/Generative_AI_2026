from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# Simple one-line prompt
prompt = PromptTemplate.from_template("{question}")

# model = ChatOpenAI()
model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0.7, max_retries=3)
parser = StrOutputParser()

# Chain: prompt → model → parser
chain = prompt | model | parser

# Run it
result = chain.invoke({"question": "What is the capital of India? give me answer in 5 words."})
print(result)
