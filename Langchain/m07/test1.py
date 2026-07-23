from fastapi import FastAPI

app = FastAPI(title="AI Chat Bot",version="1.0.0")


def db_init():
    print("database created..!")
    
@app.on_event("startup")
def startup():
    db_init()
    
@app.on_event("shutdown")
def stop():
    print("db close")
    
@app.get('/health')
def health():
    try:
        db="connected..!"
    except: 
        db="error"
    return {"status":"ok","connection":db,"version":"1.0.0"}