from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder:
    """
    Wrapper untuk model embedding multilingual.
    """
    def __init__(self, model_name: str = "distiluse-base-multilingual-cased-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_embedding_dimension()
    
    def encode(self, texts, show_progress: bool = False) -> np.ndarray:
        """
        Mengubah daftar teks menjadi vektor embedding.
        """
        return self.model.encode(texts, show_progress_bar=show_progress)