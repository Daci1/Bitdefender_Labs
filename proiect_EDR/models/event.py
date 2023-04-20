from pydantic import BaseModel

from models.verdict import HashVerdict


class DeviceModel(BaseModel):
    id: str
    os: str

class LastAccessModel(BaseModel):
    hash: str
    path: str
    pid: str


class TimeModel(BaseModel):
    m: str
    a: str

class FileModel(BaseModel):
    file_hash: str
    file_path: str
    time: TimeModel

class EventModel(BaseModel):
    device: DeviceModel
    file: FileModel
    last_access: LastAccessModel

class EventResponse(BaseModel):
    file: HashVerdict
    process: HashVerdict