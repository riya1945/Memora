from uuid import UUID
from memora.memory.store import MemoryStore
from memora.memory.retrieval import MemoryRetriever
from memora.memory.policy import MemoryPolicy
from langchain_ollama import ChatOllama

class MemoryService:
    def __init__(self, store: MemoryStore):
        self.store = store
        self.policy = MemoryPolicy()
        self.retriever = MemoryRetriever(store)
        self.classifier=ChatOllama(model="qwen3:4b",temperature=0,reasoning=False)

    def classify_category(self,content:str)-> str:
        existing=self.store.list_categories()
        prompt= f"""
You have to classify the category of the memory given. The existing categories are already stored. Reuse an existing category if it fits the memory, if it clearly fits. Create a new one only if none fits

Memory: {content}

Existing categories: {existing}

Answer with only the category, in lowercase, 1 to 3 words, no punctuation, no explanation. 
Category:

/no_think
"""
        response=self.classifier.invoke(prompt)
        return response.content.split("</think>")[-1].strip().lower()

    
    def save_memory(
        self,
        content: str,
        importance: float,
        relevance: float,
        confidence: float,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
        category: str | None = None ,
    ):
        decision = self.policy.policy_decide(
            importance, relevance, confidence
        )

        if decision == "forget":
            return None
        if category is None and self.store.use_supabase:
            category=self.classify_category(content)
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
            category=category
        )

        if decision == "archive":
            return self.store.archive_memory(returned_mem.id)

        if decision == "keep":
            self.retriever.add_memory(returned_mem)

        return returned_mem

    def update_memory(self, old_memory_id, new_memory_id):
        return self.store.update_memory(old_memory_id, new_memory_id)
