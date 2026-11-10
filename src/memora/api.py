from fastapi import FastAPI,BackgroundTasks
from pydantic import BaseModel
from memora.tools.tools import service
from memora.codespace import index_project
from memora.agent.agent import run_agent
from fastapi.staticfiles import StaticFiles

app=FastAPI()

class Indexin(BaseModel):
    root:str
    name:str

class AgentIn(BaseModel):
    message: str
    mode: str = "everyday"
    project_id: str | None = None

class MemoryIn(BaseModel):
    content: str
    importance: float = 0.9
    relevance: float = 0.9
    confidence: float = 0.9
    category: str | None = None

@app.post("/agent")
def agent(body:AgentIn):
    project_list=service.store.list_projects()
    name = "this project"
    for pro in project_list:
        if pro["id"] == body.project_id:
            name = pro["name"]
            break
    print(body.mode, name)

    if body.mode=="code":
        text = f"This is a question about the codebase of project {name}. Use search_memory with category 'codebase'.\n\n{body.message}"
    else:
        text=body.message    
    message=run_agent(text).split("</think>")[-1].strip()
    return {"answer": message}
    

@app.post("/index")
def index(body:Indexin, background_tasks:BackgroundTasks):
    background_tasks.add_task(index_project,body.root,body.name)
    return {"status": "started", "project": body.name}

@app.get("/projects")
def projects():
    return service.store.list_projects()

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


app.mount("/", StaticFiles(directory="static", html=True), name="static")