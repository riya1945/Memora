from langchain_core.tools import tool
from memora.memory.service import MemoryService

from memora.memory.store import MemoryStore

store=MemoryStore()
service=MemoryService(store)

experiments = {
    1: {"model": "Random Forest", "accuracy": 91},
    2: {"model": "XGBoost", "accuracy": 94},
    3: {"model": "Neural Network", "accuracy": 89}
}


@tool
def search_project(query):
    """Search experimental results and project performance information."""
    return "XGBoost achieved the highest accuracy of 94%"


@tool
def get_experiment(experiment_id):
    """Return the respective experiment based on the experiment id."""
    return experiments[experiment_id]



@tool
def search_memory(query):
    """Search the project's memory for relevant information."""
    return service.retriever.search(query)

@tool
def save_memory(content):
    """Save a new piece of information to memory."""
    return service.save_memory(content, importance=0.9, relevance=0.9, confidence=0.9)



@tool
def update_memory(old_memory_id, new_memory_id):
    """Archive an old memory and activate its newer replacement."""
    return service.update_memory(old_memory_id, new_memory_id)