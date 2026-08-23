from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("books/Building Machine Learning Systems with Python - Second Edition.pdf")

doc = loader.lazy_load()
i=0
for doc in loader.lazy_load():
    if i==5:
        break
    print(doc.page_content)
    i+=1    