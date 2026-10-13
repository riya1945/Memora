from memora.memory.store import MemoryStore
from memora.memory.retrieval import MemoryRetriever


def test_memory_save_and_retrieve():

    store = MemoryStore()
    retriever = MemoryRetriever(store)

    memory = store.save_memory(
        "The next version of Memora will use PostgreSQL.",
        0.9,
        0.95
    )

    retriever.add_memory(memory)

    results = retriever.search(
        "What database will the next version use?"
    )

    print("\nRetrieved:", results)

    assert results is not None
    assert len(results) > 0
    assert any(
        "PostgreSQL" in result[0].page_content
        for result in results
    )