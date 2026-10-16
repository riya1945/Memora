# before choosing which memories fit into a context window, we need
# to estimate how many tokens each memory consumes

from transformers import AutoTokenizer
class TokenCounter():
    def __init__(self):
        self.model=AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    def count_tokens(self,text):
        token_text=self.model(text,add_special_tokens=False)
        return len(token_text["input_ids"])

#tokenizer returns a dict having input ids. those ids represnt the tokens

