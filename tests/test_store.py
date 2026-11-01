
from uuid import UUID

from memora.memory.store import MemoryStore, LOCAL_OWNER_ID
from memora.memory.retrieval import MemoryRetriever, memory_to_document


def test_save_memory():
    store = MemoryStore()

    memory = store.save_memory(
        "The project uses PostgreSQL",
        importance=0.9,
        confidence=0.95,
    )

    memory2 = store.save_memory(
        "The project uses LangChain",
        importance=0.8,
        confidence=0.9,
    )

    get_mem = store.get_memory(memory2.id)
    missing = store.get_memory(UUID(int=999))

    document = memory_to_document(memory2)

    retriever = MemoryRetriever(store)
    result = retriever.build_index()
    results = retriever.search(
        "What database does the project use?"
    )

    empty_store = MemoryStore()
    empty_retriever = MemoryRetriever(empty_store)
    empty_result = empty_retriever.build_index()
    empty_results = empty_retriever.search("anything")

    assert isinstance(memory.id, UUID)
    assert memory.owner_id == LOCAL_OWNER_ID
    assert memory.content == "The project uses PostgreSQL"

    assert isinstance(memory2.id, UUID)
    assert memory2.content == "The project uses LangChain"

    assert get_mem.id == memory2.id
    assert get_mem.content == "The project uses LangChain"
    assert missing is None

    assert document.page_content == memory2.content
    assert document.metadata["id"] == str(memory2.id)
    assert document.metadata["status"] == memory2.status

    assert result is not None
    assert retriever.vector_store is not None
    assert results
    assert all(isinstance(score, float) for _, score in results)

    assert empty_result is None
    assert empty_retriever.vector_store is None
    assert empty_results == []

    archived = store.archive_memory(memory2.id)
    missing_archive = store.archive_memory(UUID(int=999))

    assert archived.id == memory2.id
    assert archived.status == "archived"
    assert missing_archive is None
    assert len(store.memory) == 2
