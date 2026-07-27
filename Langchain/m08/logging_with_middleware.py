from fastapi import FastAPI,Request
import logging
from logging.handlers import RotatingFileHandler
import time

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,# show all the logs
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            "app.log",  # file name
            maxBytes=5024,  # ikb limit
            backupCount=3,  # keep only 3 file
        ),
    ],  # cmd output
)


logger = logging.getLogger(__name__)


@app.middleware('http')
async def logging_middleware(request : Request,call_next):
    print(dict(request))
    logging.info("-----------------------------------")
    logging.info("Request Start..!")
    logging.info(f"Method : {request.method}")
    logging.info(f"Endpoint : {request.url.path}")
    
    start_time = time.time()
    
    responce = await call_next(request)
    
    end_time = time.time()
    
    duration = (end_time - start_time)*1000
    
    logging.info(f"Status Code : {responce.status_code}")
    logging.info(f"Time  : {duration:.2}")
    logging.info("Request End")
    logging.info("-----------------------------------")
    
    return responce


@app.get("/")
def home():
    logger.info("Home API is called..!!!")
    return {"message": "Home page"}


@app.get("/about")
def about():
    logging.info("insider the about API")
    return {"message": "About page"}


@app.get("/contact")
def contact():
    logging.info("insider the contact API")
    return {"message": "Contact page"}
