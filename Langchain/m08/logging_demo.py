from fastapi import FastAPI
import logging

app = FastAPI()

logging.basicConfig(
    level=logging.DEBUG,  #show all the logs
    format="%(asctime)s | %(levelname)-8s | %(message)s"
    
)
logger = logging.getLogger(__name__)

@app.get("/")
def home():
    logger.debug("⚒️ debug message...")
    
    logger.info("Home API is called..!!!")
    
    logger.warning("⚠️⚠️")
    logger.error("❌❌")
    return {
        "message":"logging deemo running..!"
    }