
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS


def memory_to_document(memory):
    return Document(
        page_content=memory.content,
        metadata={
            "id": str(memory.id),
            "created_at": memory.created_at.isoformat(),
            "status": memory.status,
        },
    )


class MemoryRetriever:
    def __init__(self, store):
        self.store = store
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = None
    def embed_memory(self,content:str) -> list[float]:
        result=self.embeddings.embed_query(content)
        return result  

    def build_index(self):
        memories = self.store.list_memories(status="active")

        if not memories:
            self.vector_store = None
            return None

        documents = [memory_to_document(mem) for mem in memories]
        self.vector_store = FAISS.from_documents(
            documents, self.embeddings
        )
        return self.vector_store

    def search(self, query, k=2):
        # Rebuild so newly saved or archived records are reflected.
        self.build_index()

        if self.vector_store is None:
            return []

        results = self.vector_store.similarity_search_with_score(
            query, k=k
        )

        active_memories = {
            str(mem.id): mem
            for mem in self.store.list_memories(status="active")
        }

        filtered_results = []

        for doc, score in results:
            memory = active_memories.get(doc.metadata["id"])

            if memory is not None:
                filtered_results.append((doc, float(score)))

        return filtered_results

    def add_memory(self, memory):
        # Keep the interface used by MemoryService.
        # Search rebuilds the index from the source of truth.
        if memory.status == "active":
            new_doc = memory_to_document(memory)

            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(
                    [new_doc], self.embeddings
                )
            else:
                self.vector_store.add_documents([new_doc])
