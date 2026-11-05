from fastapi import FastAPI
from pydantic import BaseModel
from memora.tools.tools import service
app=FastAPI()

class MemoryIn(BaseModel):
    content: str
    importance: float = 0.9
    relevance: float = 0.9
    confidence: float = 0.9
    category: str | None = None

@app.post("/memories")
def memories(body:MemoryIn):
    memory=service.save_memory(
    content=body.content,
    importance=body.importance,
    relevance=body.relevance,
    confidence=body.confidence,
    category=body.category,
)
    if memory is None:
        return {"response":"the results are not saved"}
    return {
    "id": str(memory.id),
    "content": memory.content,
    "status": memory.status,
    "category": memory.category,
}  

@app.get("/health")
def health():
    return {"status":"ok"}


@app.get("/search")
def search(q:str,category:str | None=None, k:int=5):
    results=service.retriever.search(q,k,category)
    return [
            {
                "id": doc.metadata["id"],
                "content": doc.page_content,
                "created_at": doc.metadata["created_at"],
                "score": float(score),
                "category": doc.metadata["category"]
            }
            for doc, score in results
        ]

@app.get("/categories")
def categories():
    return [{"category": c} for c in service.store.list_categories()]
