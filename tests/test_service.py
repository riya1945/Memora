from memora.memory.service import MemoryService
from memora.memory.store import MemoryStore
from memora.memory.retrieval import MemoryRetriever

def test_service():
    store=MemoryStore()
    #service=MemoryService(store)
    retriever=MemoryRetriever(store)
    memory=store.save_memory(
    "The project uses PostgreSQL"
    )
    retriever.add_memory(memory)
    re=retriever.search("Which database are we using in the project?")
    doc=re[0][0].metadata["id"]
    assert retriever.vector_store is not None
    assert doc==memory.id
    # assert service.store== store
    # assert isinstance(service.retriever, MemoryRetriever)
    # assert service.retriever.store==store
def test_add_multiple_memories():
    store=MemoryStore()
    retriever=MemoryRetriever(store)
    mem1=store.save_memory("The project uses PostgreSQL as its database.")
    mem2=store.save_memory("The project uses LangChain for its agent framework.")
    retriever.add_memory(mem1)
    retriever.add_memory(mem2)

    result=retriever.search("what framework are we using?")
    assert result[0][0].metadata["id"]==mem2.id
