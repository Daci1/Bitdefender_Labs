import functools
import os
from click import File
from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile
import motor.motor_asyncio
import uvicorn
import requests

from models.event import EventModel, EventResponse
from models.verdict import HashVerdict


app = FastAPI()

@functools.lru_cache()
def mongo_data_collection():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        os.getenv("MONGO_URL", "mongodb://root:example@localhost:27017")
    )
    print(os.getenv("MONGO_URL"))
    db=client["data"]
    collection = db["verdicts"]
    return collection

@app.post("/events")
async def verifyEvent(event: EventModel, mongo_collection=Depends(mongo_data_collection)) -> EventResponse:
    fileVerdict = await get_from_mongo(event.file.file_hash, mongo_collection=mongo_collection)
    file_risk_level = -1
    if fileVerdict is not None:
        file_risk_level = fileVerdict["risk_level"]

    processVerdict = await get_from_mongo(event.last_access.hash, mongo_collection=mongo_collection)
    process_risk_level = -1
    if processVerdict is not None:
        process_risk_level = processVerdict["risk_level"]

    file = HashVerdict(hash=event.file.file_hash, risk_level=file_risk_level)
    process = HashVerdict(hash=event.last_access.hash, risk_level=process_risk_level)
    
    verdict = EventResponse(file=file, process=process)
    return verdict

@app.post("/scan_file")
async def createVerdict(file: UploadFile, mongo_collection=Depends(mongo_data_collection)) -> str:
    url = "https://beta.nimbus.bitdefender.net/liga-ac-labs-cloud/blackbox-scanner/"
    try:
        file_content = await file.read()
        black_box_api_response = requests.post(url, files={ "file": ("file.txt", file_content)}).json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    message:str

    if black_box_api_response["hash"] is not None and black_box_api_response["risk_level"] is not None:
        message = await write_to_mongo(save_data=HashVerdict(hash=black_box_api_response["hash"], risk_level=black_box_api_response["risk_level"]), mongo_collection=mongo_collection)
    else:
        message = "Hash or risk_level missing"
    return message

async def get_from_mongo(item_hash: str, mongo_collection):
    data = await mongo_collection.find_one({"hash": item_hash})
    return data

async def write_to_mongo(save_data: HashVerdict, mongo_collection):
    await mongo_collection.insert_one(save_data.dict())
    return "Item created, hash:{}, risk_level={}".format(save_data.hash, save_data.risk_level)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)