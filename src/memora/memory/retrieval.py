from langchain_huggingface import HuggingFaceEmbeddings
from memora.memory.store import MemoryStore
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langchain_community.vectorstores import FAISS

def memory_to_document(memory):
    mem_content=memory.content
    mem_id=memory.id
    mem_created_at=memory.created_at
    mem_status=memory.status
    doc=Document(page_content=mem_content,metadata={
        "id": mem_id, "created_at":mem_created_at,"status":mem_status
    })
    return doc 

mem_to_doc_runnable=RunnableLambda(memory_to_document)

class MemoryRetriever():
    def __init__(self, store):
        self.store = store
        self.embeddings=HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
        self.vector_store = None #cause the store is empty for now
    def build_index(self):
        memories=self.store.memory
        if not memories:
            return None
        else:
         documents=[]
         for mem in memories:
            result=mem_to_doc_runnable.invoke(mem)
            documents.append(result)
         self.vector_store=FAISS.from_documents(documents,self.embeddings)    
    def search(self,query):
            if not self.vector_store:
                return None

            result=self.vector_store.similarity_search_with_score(query,k=2)
            filtered_results=[]
            for doc,score in result:
                mem_status=None

                for mem in self.store.memory:
                    if mem.id==doc.metadata["id"]:
                        mem_status=mem.status
                        break
                    if mem_status=="archived":
                        break
                if mem_status!="archived":
                    filtered_results.append((doc,score))
            return filtered_results
    
    def add_memory(self,memory):
        new_doc=mem_to_doc_runnable.invoke(memory)
        
        if self.vector_store is None:
            self.vector_store=FAISS.from_documents(
                [new_doc],self.embeddings
            )
        else:
            self.vector_store.add_documents([new_doc])    



        



def search_memory(query):
    """
    Search memory using semantic similarity and return
    relevant active memories.
    """

    results = []

    similar = vector_store.similarity_search_with_score(
        query,
        k=10
    )

    if not similar:
        return "no relevant documents"

    for doc, score in similar:

        memory_status = None

        for mem in memory:
            if mem["id"] == doc.metadata["id"]:
                memory_status = mem["status"]
                break

        if memory_status == "archived":
            continue
        print("Memory:", doc.page_content, "Score:", score)

        results.append({
            "id": doc.metadata["id"],
            "content": doc.page_content,
            "created_at": doc.metadata["created_at"].isoformat(),
            "score": float(score)
        })

    if not results:
        return "no relevant documents"

    return results
