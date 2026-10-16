from memora.memory.models import Memory
from datetime import datetime

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


class MemoryStore():
    def __init__(self):
        self.memory:list[Memory]=[]
    def save_memory(self,content,importance,confidence):
        if self.memory:
            ids = [mem.id for mem in self.memory]
            new_ids=max(ids)+1
        else:
            new_ids=1    
        created_at = datetime.now()
        new_mem=Memory(id=new_ids,content=content,created_at=created_at,status="active",importance=importance,confidence=confidence)
        self.memory.append(new_mem)
        return new_mem
    def get_memory(self,memory_id):
        for mem in self.memory:
            if mem.id==memory_id:
                return mem
        return None
    def archive_memory(self,memory_id):
        for mem in self.memory:
            if mem.id==memory_id:
                mem.status="archived"
                return mem  
        return None    

    
    def update_memory(self,old_memory_id, new_memory_id):
        old_mem=self.get_memory(old_memory_id)
        new_mem=self.get_memory(new_memory_id)
        if not old_mem or not new_mem:
            return None
        old_mem.status="archived"
        new_mem.status="active"
        return {"old_mem":old_mem,"new_mem":new_mem,"status":"updated"}
    
# def save_memory(content):
#     """Save a new memory and add it to the vector store."""

#     ids = [mem["id"] for mem in memory]
#     new_id = max(ids) + 1

#     created_at = datetime.now()

#     memory.append({
#         "id": new_id,
#         "content": content,
#         "created_at": created_at,
#         "status": "active"
#     })

#     new_document = Document(
#         page_content=content,
#         metadata={
#             "id": new_id,
#             "created_at": created_at
#         }
#     )

#     vector_store.add_documents([new_document])

#     return {
#         "id": new_id,
#         "content": content,
#         "created_at": created_at.isoformat(),
#         "status": "active"
#     }
# embeddings = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )


# vector_store = FAISS.from_documents(
#     documents,
#     embeddings
# )

# documents = []

# for mem in memory:
#     document = Document(
#         page_content=mem["content"],
#         metadata={
#             "id": mem["id"],
#             "created_at": mem["created_at"]
#         }
#     )

#     documents.append(document)
