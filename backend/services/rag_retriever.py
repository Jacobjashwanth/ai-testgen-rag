import json
import os
import numpy as np
import faiss
from typing import List, Dict, Tuple
from .embeddings import EmbeddingsService
from .file_parser import Chunk

class RAGRetriever:
    """Manage FAISS indexes and retrieve relevant chunks."""
    
    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.embeddings_service = EmbeddingsService()
        self.index_path = os.path.join(storage_path, "faiss_index.bin")
        self.metadata_path = os.path.join(storage_path, "chunks_metadata.json")
        self.index = None
        self.chunks_metadata = []
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create a new one."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'r') as f:
                self.chunks_metadata = json.load(f)
        else:
            # Create new index
            dim = self.embeddings_service.embedding_dim
            self.index = faiss.IndexFlatL2(dim)
            self.chunks_metadata = []
    
    def add_chunks(self, chunks: List[Chunk]) -> int:
        """Add chunks to the index."""
        if not chunks:
            return 0
        
        embeddings = self.embeddings_service.embed_chunks(chunks)
        self.index.add(embeddings)
        
        # Store metadata
        for chunk in chunks:
            self.chunks_metadata.append({
                'content': chunk.content,
                'source_file': chunk.source_file,
                'line_start': chunk.line_start,
                'line_end': chunk.line_end,
                'chunk_type': chunk.chunk_type,
                'name': chunk.name
            })
        
        self._save_index()
        return len(chunks)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[Chunk, float]]:
        """Retrieve top-k similar chunks for a query."""
        if self.index.ntotal == 0:
            return []
        
        query_embedding = self.embeddings_service.embed_text(query)
        query_embedding = np.array([query_embedding])
        
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0:  # Valid index
                metadata = self.chunks_metadata[idx]
                chunk = Chunk(
                    content=metadata['content'],
                    source_file=metadata['source_file'],
                    line_start=metadata['line_start'],
                    line_end=metadata['line_end'],
                    chunk_type=metadata['chunk_type'],
                    name=metadata['name']
                )
                distance = float(distances[0][i])
                # Convert L2 distance to similarity score (0-1 range)
                similarity = 1.0 / (1.0 + distance)
                results.append((chunk, similarity))
        
        return results
    
    def _save_index(self):
        """Save index and metadata to disk."""
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'w') as f:
            json.dump(self.chunks_metadata, f, indent=2)
    
    def clear_index(self):
        """Clear the index."""
        dim = self.embeddings_service.embedding_dim
        self.index = faiss.IndexFlatL2(dim)
        self.chunks_metadata = []
        self._save_index()
