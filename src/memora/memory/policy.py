

class MemoryPolicy():
    def policy_decide(self,importance,relevance,confidence):
        score=importance*0.75+relevance*0.8+confidence*0.9
        if score>=2:
            return "keep"
        elif score>=1.5:
            return "archive"
        else:
            return "forget"      
        