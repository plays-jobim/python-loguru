from typing import Union
from fastapi import FastAPI

from loguru import logger
import logging
from logger import init_logging

app = FastAPI()

init_logging()

@app.get("/")
def read_root():
    logger.info("read_root")
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    logger.info("read_item GET")
    return {"item_id": item_id, "q": q}

@app.post("/items/")
def read_item(item_id: int, q: Union[str, None] = None):
    logger.info("read_root POST")
    return {"item_id": item_id, "q": q}
