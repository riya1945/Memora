from uuid import UUID

from langchain_core.tools import tool

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
def search_memory(query: str):
    """Search the project's memory for relevant information."""
    results = service.retriever.search(query)

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
