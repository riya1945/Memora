
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


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
