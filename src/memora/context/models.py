from pydantic import BaseModel
from memora.memory.models import Memory

class ContextItem(BaseModel):
    memory: Memory
    relevance:float
    recency:float
    token_cost:int
    score: float
    