

class ContextBudget():
    def __init__(self,maximum,reserved):
        self.maximum=maximum
        self.reserved=reserved
    def available_tokens(self):
        if self.maximum>=self.reserved:
         remaining=self.maximum-self.reserved
        else:
           return None
        return remaining