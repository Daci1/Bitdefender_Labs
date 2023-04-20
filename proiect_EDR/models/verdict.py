from pydantic import BaseModel

class HashVerdict(BaseModel):
    hash: str
    risk_level: int