from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_batch(self, texts):
        return self.model.encode(texts)

    def embed_query(self, text):
        return self.model.encode(text)
