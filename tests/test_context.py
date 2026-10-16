from memora.context.manager import ContextManager
from memora.context.tokenizer import TokenCounter
from memora.memory.retrieval import MemoryRetriever
from memora.memory.store import MemoryStore
from memora.context.budget import ContextBudget
from memora.memory.service import MemoryService

def test_context():
    store=MemoryStore()
    retriever=MemoryRetriever(store)
    token_counter=TokenCounter()
    budget=ContextBudget(maximum=1000,reserved=200)
    budget2=ContextBudget(maximum=500,reserved=500)
    context=ContextManager(budget,token_counter,retriever)
    context2=ContextManager(budget2,token_counter,retriever)
    budget3 = ContextBudget(maximum=20, reserved=13)
    service = MemoryService(store)
    service.retriever = retriever 
    context3 = ContextManager(budget3, token_counter, retriever)
    budget4 = ContextBudget(maximum=40, reserved=9)
    context4 = ContextManager(budget4, token_counter, retriever) 
    service.save_memory(
    "we are using python as a language",
    importance=0.8,
relevance=1.0,
confidence=0.8
)
    service.save_memory(
        "Room available for rent in sbioa unity enclave for 8.7k per month from November 1st Two roommates are already present Dm for more details",
        importance=0.98,
    relevance=1.0,
    confidence=0.9
    )
    short_cost = token_counter.count_tokens("we are using python as a language")
    long_cost = token_counter.count_tokens("Room available for rent in sbioa unity enclave for 8.7k per month from November 1st Two roommates are already present Dm for more details")

    check_mem=context.select_context("what do i know?")
    
    assert len(check_mem)==2    
    formatted_context = context.format_context(check_mem)

    assert isinstance(formatted_context, str)
    assert "we are using python as a language" in formatted_context
    assert "\n" in formatted_context
    check_second_mem=context2.select_context("is there additional info?")
    assert len(check_second_mem)==0
    check_third_mem = context3.select_context("what do i know?")
    assert len(check_third_mem) == 1
    check_fourth_mem = context4.select_context("what do i know?")

    assert len(check_fourth_mem) == 1
    assert check_fourth_mem[0].memory.content == "we are using python as a language"

    