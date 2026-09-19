from memora.memory.store import save_memory
from memora.memory.retrieval import search_memory


def test_memory_save_and_retrieve():

    save_memory(
        "The next version of Memora will use PostgreSQL."
    )

    results = search_memory(
        "What database will the next version use?"
    )

    print("\nRetrieved:", results)

    assert results != "no relevant documents"
    assert any(
        "PostgreSQL" in result["content"]
        for result in results
    )