from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("books/Building Machine Learning Systems with Python - Second Edition.pdf")

doc = loader.load()

# print(len(doc))

# print(doc[0])

# print(dir(doc[0]))  

# print(type(doc[0]))

print(doc[4].page_content)
print("-"*90)
print(doc[4].metadata)

