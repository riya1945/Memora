from memora.memory.store import MemoryStore
from memora.memory.retrieval import mem_to_doc_runnable,MemoryRetriever

def test_save_memory():
    store=MemoryStore()
    memory = store.save_memory(
    "The project uses PostgreSQL",
    importance=0.9,
    confidence=0.95
)

    memory2 = store.save_memory(
    "The project uses Langchain",
    importance=0.8,
    confidence=0.9
)
    get_mem=store.get_memory(memory2.id)
    result = store.get_memory(999)
    runn=mem_to_doc_runnable.invoke(memory2)
    retriever=MemoryRetriever(store)
    result2=retriever.build_index()
    results=results = retriever.search("What database does the project use?")
    empty_store=MemoryStore()
    empty_re=MemoryRetriever(empty_store)
    empty_result=empty_re.build_index()

    empty_results = empty_re.search("anything")

    assert memory.id==1
    assert memory.content=="The project uses PostgreSQL"
    assert memory2.id==2
    assert memory2.content=="The project uses Langchain"
    assert get_mem.id==2
    assert get_mem.content=="The project uses Langchain"
    assert result is None 
    assert runn.page_content==memory2.content
    assert runn.metadata["id"] == memory2.id
    assert runn.metadata["status"] == memory2.status
    archived = store.archive_memory(memory2.id)
    missing=store.archive_memory(999)
    
    assert retriever.vector_store is not None
    assert results[0][0].metadata["id"]==memory.id
    assert empty_re.vector_store is None
    assert empty_results is None
    assert archived.id==memory2.id
    assert archived.status=="archived"
    assert missing is None
    assert len(store.memory)==2