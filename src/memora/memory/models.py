from pydantic import BaseModel
from datetime import datetime

class Memory(BaseModel):
    id:int
    content:str
    created_at:datetime
    status:str
    importance: float
    confidence: float
