
from datetime import datetime
from uuid import UUID
import json
from pydantic import BaseModel,field_validator


class Memory(BaseModel):
    id: UUID
    owner_id: UUID
    project_id: UUID | None = None
    content: str
    created_at: datetime
    updated_at: datetime
    status: str
    importance: float
    confidence: float
    category: str | None = None
    embedding: list[float] | None=None
    @field_validator("embedding",mode="before")
    @classmethod
    def parse_embedding(cls,value):
        if isinstance(value,str):
            float=json.loads(value)
            return float
        return value
    


