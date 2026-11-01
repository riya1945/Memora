
from uuid import UUID

from memora.memory.store import MemoryStore
from memora.memory.retrieval import MemoryRetriever
from memora.memory.policy import MemoryPolicy


class MemoryService:
    def __init__(self, store: MemoryStore):
        self.store = store
        self.policy = MemoryPolicy()
        self.retriever = MemoryRetriever(store)

    def save_memory(
        self,
        content: str,
        importance: float,
        relevance: float,
        confidence: float,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
    ):
        decision = self.policy.policy_decide(
            importance, relevance, confidence
        )

        if decision == "forget":
            return None
        embedding = (
        self.retriever.embed_memory(content)
        if self.store.use_supabase and decision == "keep"
        else None
)
        returned_mem = self.store.save_memory(
            content=content,
            importance=importance,
            confidence=confidence,
            owner_id=owner_id,
            project_id=project_id,
            embedding=embedding,
        )

        if decision == "archive":
            return self.store.archive_memory(returned_mem.id)

        if decision == "keep":
            self.retriever.add_memory(returned_mem)

        return returned_mem

    def update_memory(self, old_memory_id, new_memory_id):
        return self.store.update_memory(old_memory_id, new_memory_id)
