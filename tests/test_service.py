
from memora.memory.service import MemoryService
from memora.memory.store import MemoryStore
from memora.memory.retrieval import MemoryRetriever
from memora.tools.tools import save_memory, search_memory, service
from memora.context.manager import ContextManager
from memora.context.budget import ContextBudget
from memora.context.tokenizer import TokenCounter


def test_service():
    store = MemoryStore()
    memory_service = MemoryService(store)

    memory = store.save_memory(
        "The project uses PostgreSQL",
        importance=0.9,
        confidence=0.95,
    )

    memory_service.retriever.add_memory(memory)

    results = memory_service.retriever.search(
        "Which database are we using in the project?"
    )

    assert results

    retrieved_memory_id = results[0][0].metadata["id"]

    new_memory = memory_service.save_memory(
        "The project is using Python as a language",
        importance=0.9,
        relevance=0.9,
        confidence=0.95,
    )

    language_results = memory_service.retriever.search(
        "What language are we using for the project?"
    )

    assert any(
        document.metadata["id"] == str(new_memory.id)
        for document, score in language_results
    )

    assert memory_service.retriever.vector_store is not None
    assert retrieved_memory_id == str(memory.id)


def test_add_multiple_memories():
    store = MemoryStore()
    retriever = MemoryRetriever(store)

    mem1 = store.save_memory(
        "The project uses PostgreSQL as its database.",
        importance=0.7,
        confidence=0.8,
    )

    mem2 = store.save_memory(
        "The project uses LangChain for its agent framework.",
        importance=0.9,
        confidence=0.95,
    )

    retriever.add_memory(mem1)
    retriever.add_memory(mem2)

    results = retriever.search("What framework are we using?")

    assert results
    assert results[0][0].metadata["id"] == str(mem2.id)


def test_service_with_update():
    store = MemoryStore()
    memory_service = MemoryService(store)

    mem1 = store.save_memory(
        "The project uses PostgreSQL as its database.",
        importance=0.7,
        confidence=0.8,
    )

    mem2 = store.save_memory(
        "The project uses LangChain for its agent framework.",
        importance=0.9,
        confidence=0.95,
    )

    updated_result = memory_service.update_memory(mem1.id, mem2.id)

    assert updated_result["status"] == "updated"
    assert mem1.status == "archived"
    assert mem2.status == "active"


def test_tool_save_and_search_mem():
    saved_memory = save_memory.invoke({
        "content": "Memora uses PostgreSQL for persistent storage."
    })

    search_results = search_memory.invoke({
        "query": "which database are we using for persistent storage?"
    })

    assert saved_memory is not None
    assert any(
        item["content"] == "Memora uses PostgreSQL for persistent storage."
        for item in search_results
    )

    context_budget = ContextBudget(maximum=4096, reserved=512)
    token_counter = TokenCounter()

    context_manager = ContextManager(
        budget=context_budget,
        token_counter=token_counter,
        retriever=service.retriever,
    )

    selected_context = context_manager.select_context(
        "Which database does Memora use for persistent storage?"
    )

    assert any(
        item.memory.content == "Memora uses PostgreSQL for persistent storage."
        for item in selected_context
    )
