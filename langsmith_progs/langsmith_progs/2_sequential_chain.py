# from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

os.environ['LANGCHAIN_PROJECT'] = 'Seq LLM app_weekend'

load_dotenv()

prompt1 = PromptTemplate(
    template='Generate a detailed report on {topic}',
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template='Generate a 5 pointer summary from the following text \n {text}',
    input_variables=['text']
)

# model = ChatOpenAI()
# model1 = ChatGroq(model="groq/compound", temperature=0.7, max_retries=3)
# model2 = ChatGroq(model="groq/compound", temperature=0.7, max_retries=3)
# model1 = ChatGroq(model="meta-llama/llama-prompt-guard-2-22m", temperature=0.7, max_retries=3)
# model2 = ChatGroq(model="meta-llama/llama-prompt-guard-2-22m", temperature=0.7, max_retries=3)
model1 = ChatGroq(model="qwen/qwen3.8-27b", temperature=0.7, max_retries=3)
model2 = ChatGroq(model="qwen/qwen3.8-27b", temperature=0.7, max_retries=3)

parser = StrOutputParser()

chain = prompt1 | model1 | parser | prompt2 | model2 | parser

config = {
    'tags': ['sequential_chain', 'llm', 'groq','summarization','report generation'],
    'metadata': {'model1': 'qwen/qwen3.6-27b', 'model2': 'qwen/qwen3.6-27b', 'model1_temperature': 0.7, 'model2_temperature': 0.7, 
                 'max_retries': 3, 'parser': 'StrOutputParser'}
}

result = chain.invoke({'topic': 'Unemployment in India in 100 words'}, config=config)

print(result)
