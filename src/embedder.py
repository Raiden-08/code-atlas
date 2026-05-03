from sentence_transformers import SentenceTransformer


class Embedder:
    """
    Singleton-style embedder.
    Loads the model once per process and reuses it.
    """
    _model = None

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        if Embedder._model is None:
            Embedder._model = SentenceTransformer(model_name)
        self.model = Embedder._model

    def embed_batch(self, texts):
        return self.model.encode(texts, show_progress_bar=False)

    def embed_query(self, text):
        return self.model.encode(text)
