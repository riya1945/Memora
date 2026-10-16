from memora.memory.store import MemoryStore
from memora.memory.retrieval import MemoryRetriever


def test_memory_save_and_retrieve():

    store = MemoryStore()
    retriever = MemoryRetriever(store)

    memory = store.save_memory(
        "The next version of Memora will use PostgreSQL.",
        0.7,
        0.95
    )
    memory2=store.save_memory(
        "We use MongoDB as the project database",0.9,0.99
    )
    retriever.add_memory(memory)

    results = retriever.search(
        "What database will the next version use?"
    )

    print("\nRetrieved:", results)
    updated_result=store.update_memory(memory.id,memory2.id)

    print(updated_result)
    assert results is not None
    assert len(results) > 0
    assert any(
        "PostgreSQL" in result[0].page_content
        for result in results
    )
    assert memory.status=="archived"
    assert memory2.status=="active"
