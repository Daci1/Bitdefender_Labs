from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

import uvicorn

app = FastAPI()

class Item(BaseModel):
    id: int
    description: str

@app.post("/createItem")
def createItem(item: Item):
    return item
    

@app.get("/")
def read_root(message: str = ""):
    if message != "":
        return {"message": message}
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
