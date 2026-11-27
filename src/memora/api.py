from fastapi import FastAPI,BackgroundTasks,HTTPException
from pydantic import BaseModel
from memora.tools.tools import service
from memora.codespace import index_project,apply_edit
from memora.agent.agent import run_agent
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone


app=FastAPI()

class Indexin(BaseModel):
    root:str
    name:str
class ApplyEditIn(BaseModel):
    project_id:str
    user_path:str
    new_content:str
    expected_old_hash: str


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
def agent(body: AgentIn):

    request_started_at = datetime.now(timezone.utc)

    if body.mode == "code":
        if not body.project_id:
            raise HTTPException(
                status_code=400,
                detail="Project ID is required"
            )

        project_name = service.store.get_project(body.project_id)

        if not project_name:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )

        name = project_name["name"]
        root_path = project_name["root_path"]

        text = (
            f"This is a question about the codebase of project {name}. "
            "Use search_memory with category 'codebase'.\n\n"
            f"{body.message}"
        )
    else:
        text = body.message

    result = run_agent(
        text,
        mode=body.mode,
        project_root=root_path if body.mode == "code" else None,
        project_id=body.project_id
    )

    messages = result["messages"]
    message = messages[-1].content.split("</think>")[-1].strip()

    proposals = []

    if body.mode == "code":
        proposals = service.store.list_pending_proposals(
            body.project_id,
            created_after=request_started_at
        )

    proposal_data = [
        {
            "id": p["id"],
            "user_path": p["user_path"],
            "diff": p["diff"],
            "status": p["status"],
            "created_at": p["created_at"]
        }
        for p in proposals
    ]

    return {
        "answer": message,
        "proposals": proposal_data
    }

    

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

@app.post("/apply_edit")
def apply_edit_endpoint(body:ApplyEditIn):
    project = service.store.get_project(body.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    root_path = project["root_path"]
    result=apply_edit(root_path,body.user_path,body.new_content,body.expected_old_hash)
    return {"result": result}

@app.post("/proposals/{proposal_id}/approve")
def approve(proposal_id: str):
    proposal=service.store.get_edit_proposal(proposal_id)
    if not proposal:
        raise HTTPException(404,"Proposal not found")
    if proposal["status"]!="pending":
        raise HTTPException(409,"Proposal is not pending")
    project_root=service.store.get_project_root(project_id=proposal["project_id"])
    if not project_root:
        raise HTTPException(400, "Project has no stored root")
    edit=apply_edit(project_root,proposal["user_path"],proposal["new_content"],proposal["original_hash"])
    if edit.startswith("Successfully"):
        service.store.update_edit_proposal_status(proposal_id,"applied")
        return {"status":"applied","message":edit}
    else:
        raise HTTPException(409,edit)

@app.post("/proposals/{proposal_id}/reject")
def reject(proposal_id: str):
    proposal = service.store.get_edit_proposal(proposal_id)
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    if proposal["status"] != "pending":
        raise HTTPException(409, "Proposal is not pending")

    updated = service.store.update_edit_proposal_status(proposal_id, "rejected")
    if not updated:
        raise HTTPException(409, "Proposal is not pending")

    return {"status": "rejected"}

app.mount("/", StaticFiles(directory="static", html=True), name="static")