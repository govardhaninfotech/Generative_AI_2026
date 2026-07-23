from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import time
app = FastAPI(title="AI Chat API",version="1.0.2")


def intit_db():
    print("database connected..")

@app.on_event("startup")
def startup():
    intit_db()
    
@app.on_event("shutdown")
def stop():
    print("server close..!")

@app.get("/chat")
async def chat_stream():
    chats = ["hello! how can i help you today?",
             "i am a ai",
             "you can ask me anythig",
             "let me know if you need any help..!"]
    async def generate():
        start = time.time()
        full_res=''
        for chunk in chats:
            yield f"data : {chunk}\n\n"
            asyncio.sleep(20)
            print(time.localtime())
            full_res += chunk
        duration = (time.time()-start)*1000
        yield "data : [DOEN]\n\n"
    return StreamingResponse(generate(),media_type="text/event-stream")
            


    
@app.get('/health')
def health():
    try:
        db="connected..!"
    except: 
        db="error"
    return {"status":"ok","connection":db,"version":"1.0.0"}    
