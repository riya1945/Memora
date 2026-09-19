
from memora.memory.store import memory, vector_store


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
