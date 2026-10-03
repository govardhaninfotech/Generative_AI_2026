# pip install -U langchain langchain-openai langchain-community faiss-cpu pypdf python-dotenv
# python -m pip install --upgrade pip 

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter# from langchain_openai import OpenAIEmbeddings
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

load_dotenv()  

os.environ['LANGCHAIN_PROJECT'] = 'RAG_app_1'


PDF_PATH = "islr.pdf"  # <-- change to your PDF filename
print(PDF_PATH)

# 1) Load PDF
loader = PyPDFLoader(PDF_PATH)
docs = loader.load()  # one Document per page
print("data loaded...")

# 2) Chunk
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
splits = splitter.split_documents(docs)

print(f"Total chunks: {len(splits)}")
# 3) Embed + index
# emb = OpenAIEmbeddings(model="text-embedding-3-small")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vs = FAISS.from_documents(splits, embeddings)

retriever = vs.as_retriever(search_type="similarity", search_kwargs={"k": 4})
print("retriever ready...")
# 4) Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer ONLY from the provided context. If not found, say you don't know."),
    ("human", "Question: {question}\n\nContext:\n{context}")
])
print("prompt ready...")
# 5) Chain
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# llm = ChatGroq(model="groq/compound", temperature=0.7, max_retries=3)
llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0.7, max_retries=3)
def format_docs(docs): return "\n\n".join(d.page_content for d in docs)

parallel = RunnableParallel({
    "context": retriever | RunnableLambda(format_docs),
    "question": RunnablePassthrough()
})

chain = parallel | prompt | llm | StrOutputParser()

# 6) Ask questions
print("PDF RAG ready. Ask a question (or Ctrl+C to exit).")
#q = input("\nQ: ")
q = "Who is the author of the book?"
ans = chain.invoke(q.strip())
print("\nA:", ans)
