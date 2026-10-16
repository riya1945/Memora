from memora.context.tokenizer import TokenCounter
from memora.context.budget import ContextBudget
from datetime import datetime
import math
from memora.memory.retrieval import MemoryRetriever
from memora.context.models import ContextItem

class ContextManager():
    def __init__(self,budget:ContextBudget,token_counter:TokenCounter,retriever: MemoryRetriever):
        self.token_counter=token_counter
        self.budget=budget
        self.retriever = retriever

    def select_context(self,query):
        results=self.retriever.search(query)
        if results is None:
            return []
        candidates=[]
        for doc,distance in results:
            mem=self.retriever.store.get_memory(doc.metadata["id"])
            if mem is None:
                continue
            relevance=1/(1+distance)
            token_cost=self.token_counter.count_tokens(mem.content)
            
            age=datetime.now()-mem.created_at
            age_sec=age.total_seconds()
            age_to_days=age_sec/86400
            decay_rate=math.log(2)/7 # 7 day half life
            recency=math.exp(-decay_rate*age_to_days)
            score=0.4*relevance+0.25*mem.importance+0.2*mem.confidence+0.15*recency
    
            candidates.append(
    ContextItem(
        memory=mem,
        relevance=relevance,
        recency=recency,
        token_cost=token_cost,
        score=score
    )
)
            
        candidates.sort(
    key=lambda candidate: candidate.score / max(candidate.token_cost, 1),
    reverse=True
)
        remaining_tokens=self.budget.available_tokens()
        selected_context=[]
        for candidate in candidates:
            if candidate.token_cost<=remaining_tokens:
                selected_context.append(candidate)
                remaining_tokens-=candidate.token_cost

        return selected_context        
    def format_context(self, selected_context):
        if not selected_context:
            return ""

        context_text = "\n".join(
        item.memory.content for item in selected_context
    )

        return f"Relevant memories:\n{context_text}"
            


