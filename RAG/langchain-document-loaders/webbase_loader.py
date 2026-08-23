from langchain_community.document_loaders import WebBaseLoader
# from bs4 import BeautifulSoup
# from langchain_openai import ChatOpenAI
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts import PromptTemplate
# from dotenv import load_dotenv

# load_dotenv() 

# model = ChatOpenAI()

# prompt = PromptTemplate(
#     template='Answer the following question \n {question} from the following text - \n {text}',
#     input_variables=['question','text']
# )

# parser = StrOutputParser()

# url = 'https://www.flipkart.com/apple-macbook-air-m2-16-gb-256-gb-ssd-macos-sequoia-mc7x4hn-a/p/itmdc5308fa78421'
url = "https://www.amazon.in/Samsung-Smartphone-Silverblue-Snapdragon-ProVisual/dp/B0DSKNKCYX/ref=sr_1_1_sspa?adgrpid=1321614610108232&dib=eyJ2IjoiMSJ9.VQt1TvbYMygRxkBWvNL-7mvZIZa4ENV90nzeckFrVZXVHm3Nghp_GEKIiyKHElX3bgIM-77fojBLCg9SBA2lNWhLD1HRVMR1qHaH-XJs5qb8DfOo7EafKL-PLxoT_d-47D4u2i3jucIO6a6BJBgWqil--O6-ZxyW0cWXotzb6cICCYDGRy1FRIoxbLxF3DNz-eIOxsPGnTWvtQRj9_xNzTwj4_dwTHIVyncvaDWSGfM.wXuI6OseV2NZ99BcFcGpNZDlP5NKaV-4YGOpSu0qbHQ&dib_tag=se&hvadid=82601181840479&hvbmt=be&hvdev=c&hvlocphy=155451&hvnetw=o&hvqmt=e&hvtargid=kwd-82601817825301%3Aloc-90&hydadcr=24566_2369365&keywords=samsung%2Bs25%2Bultra&mcid=1e5b82d788de38db91ed0d968cbcf332&qid=1786367137&sr=8-1-spons&aref=njAVNlLzIx&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1"
loader = WebBaseLoader(url)

docs = loader.load()

print(docs)
# for i in docs:
    # print(i)
# chain = prompt | model | parser

# print(chain.invoke({'question':'What is the prodcut that we are talking about?', 'text':docs[0].page_content}))
