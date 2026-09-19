from langchain_core.tools import tool

from memora.memory.store import (
    memory,
    save_memory as store_memory,
    update_memory as update_memory_store
)
from memora.memory.retrieval import search_memory as retrieve_memory



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
    return retrieve_memory(query)

@tool
def save_memory(content):
    """Save a new piece of information to memory."""
    return store_memory(content)


@tool
def update_memory(old_memory_id, new_memory_id):
    """Archive an old memory and activate its newer replacement."""
    return update_memory_store(old_memory_id, new_memory_id)