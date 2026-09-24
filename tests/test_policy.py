from memora.memory.policy import MemoryPolicy
from memora.memory.store import MemoryStore
from memora.memory.service import MemoryService


def test_policy():
    policy=MemoryPolicy()
    result=policy.policy_decide(0.9,0.9,0.9)
    assert result=="keep"
def test_keep_memory():
    store = MemoryStore()
    service = MemoryService(store)

    memory = service.save_memory(
        "The project uses PostgreSQL",
        importance=0.9,
        relevance=0.9,
        confidence=0.9
    )

    assert memory is not None
    assert len(store.memory) == 1
    assert memory.status == "active"
    assert store.get_memory(memory.id) == memory


def test_archive_memory():
    store = MemoryStore()
    service = MemoryService(store)

    memory = service.save_memory(
        "The project previously used MySQL",
        importance=0.65,
        relevance=0.65,
        confidence=0.65
    )

    assert memory is not None
    assert len(store.memory) == 1
    assert memory.status == "archived"
    assert store.get_memory(memory.id) == memory


def test_forget_memory():
    store = MemoryStore()
    service = MemoryService(store)

    memory = service.save_memory(
        "Random irrelevant information",
        importance=0.1,
        relevance=0.1,
        confidence=0.1
    )

    assert memory is None
    assert len(store.memory) == 0