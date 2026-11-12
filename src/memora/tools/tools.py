from uuid import UUID

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from memora.memory.service import MemoryService
from memora.memory.store import MemoryStore


store = MemoryStore(use_supabase=True)
service = MemoryService(store)

experiments = {
    1: {"model": "Random Forest", "accuracy": 91},
    2: {"model": "XGBoost", "accuracy": 94},
    3: {"model": "Neural Network", "accuracy": 89},
}


@tool
def search_project(query: str):
    """Search experimental results and project performance information."""
    return "XGBoost achieved the highest accuracy of 94%"


@tool
def get_experiment(experiment_id: int):
    """Return the respective experiment based on the experiment id."""
    return experiments.get(experiment_id, {"error": "Experiment not found"})


@tool
def search_memory(query: str,category:str |None=None,k:int=5):
    """Search memory for relevant information.
    category: optional topic tag such as 'fitness'. Only use it if you got
    the tag from list_categories. Leave it empty to search all memories.

    The 'codebase' category contains summaries of the project's source files. Use category='codebase' for questions about code, such as which file does what."""
    results = service.retriever.search(query,category=category,k=k)
    if category and not results:
        results=service.retriever.search(query,k=k)

    return [
        {
            "id": doc.metadata["id"],
            "content": doc.page_content,
            "created_at": doc.metadata["created_at"],
            "score": float(score),
        }
        for doc, score in results
    ]

@tool
def list_categories():
    """List the topic tags that exist in memory, e.g. before filtering a search by category."""
    return service.store.list_categories()

@tool
def save_memory(content: str):
    """Save a new piece of information to memory."""
    memory = service.save_memory(
        content,
        importance=0.9,
        relevance=0.9,
        confidence=0.9,
    )

    if memory is None:
        return {"status": "not_saved", "reason": "Memory policy chose to forget"}

    return {
        "id": str(memory.id),
        "content": memory.content,
        "status": memory.status,
    }


@tool
def update_memory(old_memory_id: str, new_memory_id: str):
    """Archive an old memory and activate its newer replacement."""
    try:
        old_id = UUID(old_memory_id)
        new_id = UUID(new_memory_id)
    except ValueError:
        return {"error": "Memory IDs must be valid UUIDs"}

    result = service.update_memory(old_id, new_id)

    if result is None:
        return {"error": "One or both memories were not found"}

    return {
        "status": result["status"],
        "old_memory_id": str(result["old_mem"].id),
        "new_memory_id": str(result["new_mem"].id),
    }

@tool
def read_project_file(user_path: str, config: RunnableConfig) -> str:
    """Read a file from the currently selected project."""
    project_root=config.get("configurable", {}).get("project_root")
    if not project_root:
        return "No project is currently selected."
    from memora.codespace import read_file  # to avoid circular import
    file=read_file(project_root,user_path,max_chars=8000)
    return file


