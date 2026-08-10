from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader('books/Building Machine Learning Systems with Python - Second Edition.pdf')

docs = loader.load()

print(len(docs))

print(docs[5].page_content)
print(docs[5].metadata)