from memora.memory.store import MemoryStore
from memora.memory.retrieval import MemoryRetriever



class MemoryService():
    def __init__(self,store):
        self.store=store
        self.retriever=MemoryRetriever(store)