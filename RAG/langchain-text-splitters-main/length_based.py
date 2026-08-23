# with old version of langchain 
# from langchain.text_splitter import CharacterTextSplitter
# with new version of langchain 
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader('connectpdf_dummy_10page.pdf')

docs = loader.load()

splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=0,
    separator=''
)

result = splitter.split_documents(docs)

print(result[1].page_content)