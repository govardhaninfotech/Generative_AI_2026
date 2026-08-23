from langchain_community.document_loaders import TextLoader

loader = TextLoader('cricket.txt', encoding='utf-8')

doc = loader.load()

print(type(doc))

print(len(doc))

print(type(doc[0]))

# print(dir(doc[0]))
print(doc[0].page_content)
print(doc[0].metadata)