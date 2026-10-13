from memora.memory.service import MemoryService
from memora.memory.store import MemoryStore
from memora.memory.retrieval import MemoryRetriever


def test_service():
    store = MemoryStore()
    service = MemoryService(store)

    memory = store.save_memory(
        "The project uses PostgreSQL",
        importance=0.9,
        confidence=0.95
    )

    service.retriever.add_memory(memory)

    results = service.retriever.search(
        "Which database are we using in the project?"
    )

    retrieved_memory_id = results[0][0].metadata["id"]

    new_memory = service.save_memory(
        "The project is using Python as a language",
        importance=0.9,
        relevance=0.9,
        confidence=0.95
    )

    language_results = service.retriever.search(
        "What language are we using for the project?"
    )

    assert any(
        document.metadata["id"] == new_memory.id
        for document, score in language_results
    )

    assert service.retriever.vector_store is not None
    assert retrieved_memory_id == memory.id


def test_add_multiple_memories():
    store = MemoryStore()
    retriever = MemoryRetriever(store)

    mem1 = store.save_memory(
        "The project uses PostgreSQL as its database.",
        importance=0.9,
        confidence=0.95
    )

    mem2 = store.save_memory(
        "The project uses LangChain for its agent framework.",
        importance=0.9,
        confidence=0.95
    )

    retriever.add_memory(mem1)
    retriever.add_memory(mem2)

    results = retriever.search("What framework are we using?")

    assert results is not None
    assert len(results) > 0
    assert results[0][0].metadata["id"] == mem2.id