from memora.memory.store import MemoryStore
from memora.memory.retrieval import MemoryRetriever
from memora.memory.policy import MemoryPolicy


class MemoryService():
    def __init__(self,store):
        self.store=store
        self.policy=MemoryPolicy()
        self.retriever=MemoryRetriever(store)
    def save_memory(self,content,importance,relevance,confidence):
            decision=self.policy.policy_decide(importance,relevance,confidence)
            if decision=="keep":
                 returned_mem=self.store.save_memory(content,importance,confidence)
                 self.retriever.add_memory(returned_mem)
            elif decision=="archive":
                 returned_mem=self.store.save_memory(content,importance,confidence)
                 self.store.archive_memory(returned_mem.id)
            elif decision=="forget":
                 return None     
                      

            return returned_mem
    def update_memory(self,old_memory_id,new_memory_id):
         updated_result=self.store.update_memory(old_memory_id,new_memory_id)
         return updated_result
         
    