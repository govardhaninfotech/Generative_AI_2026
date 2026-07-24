from fastapi import FastAPI
import logging
from logging.handlers import RotatingFileHandler

app = FastAPI()

file_handler = RotatingFileHandler(
    "app.log",  # file name
    maxBytes=1024,  # ikb limit
    backupCount=3,  # keep only 3 file
)


formmter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")

file_handler.setFormatter(formmter)

logging.basicConfig(
    level=logging.INFO,  # show all the logs
    handlers=[logging.StreamHandler(), file_handler],  # cmd output
)


logger = logging.getLogger(__name__)


@app.get("/")
def home():
    logger.debug("⚒️ debug message...")

    logger.info("Home API is called..!!!")

    logger.warning("show warrning")
    logger.error("show error")

    return {"message": "logging deemo running..!"}
