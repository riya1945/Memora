from memora.memory.store import save_memory,update_memory
from memora.memory.retrieval import search_memory
from memora.memory.store import memory

def test_mem_and_search():
    old_mem = save_memory("The project uses Supabase as the database.")
    new_mem = save_memory("The project will use PostgreSQL as the database.") 
    old_ids=old_mem["id"]
    new_ids=new_mem["id"]
    update=update_memory(old_ids,new_ids)

    results = search_memory(
    "What database does the project use?"
)
    
    
    assert results != "no relevant documents"
    assert any(
    result["id"] == new_ids
    for result in results
)

    assert not any(
    result["id"] == old_ids
    for result in results
)