import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List
import os

class EmbeddingsService:
    """Generate and manage embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def embed_chunks(self, chunks) -> np.ndarray:
        """Embed a list of chunks and return embeddings array."""
        texts = [chunk.content for chunk in chunks]
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.astype(np.float32)
    
    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text query."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Embed multiple texts."""
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.astype(np.float32)
