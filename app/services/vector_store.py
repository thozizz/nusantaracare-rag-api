import faiss
import numpy as np
import pickle
from typing import List, Dict, Any, Optional
from .embedder import Embedder

class VectorStore:
    """
    Vector store dengan FAISS (IndexFlatL2) + metadata.
    """
    def __init__(self, embedder: Embedder):
        self.embedder = embedder
        self.dimension = embedder.dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []  # list of chunk dicts
        self.index_path = None
        self.metadata_path = None

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Menambahkan daftar chunk ke indeks.
        Setiap chunk harus memiliki key: 'text', 'chunk_id', 'metadata', 'section_title'.
        """
        texts = [chunk['text'] for chunk in chunks]
        vectors = self.embedder.encode(texts, show_progress=True)
        self.index.add(np.array(vectors).astype('float32'))
        self.metadata.extend(chunks)

    def search(self, query: str, k: int = 3, 
               filter_active: bool = True, 
               distance_threshold: Optional[float] = None) -> List[Dict]:
        """
        Mencari chunk paling relevan berdasarkan query.
        - filter_active: jika True, hanya mengambil chunk dengan is_active=True
        - distance_threshold: batas maksimum jarak L2 (semakin kecil semakin mirip)
        """
        query_vec = self.embedder.encode([query])[0]  # shape (dim,)
        query_vec = np.array([query_vec]).astype('float32')
        distances, indices = self.index.search(query_vec, k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            chunk = self.metadata[idx]
            if filter_active and not chunk['metadata'].get('is_active', True):
                continue
            if distance_threshold is not None and dist > distance_threshold:
                continue
            results.append({
                "chunk": chunk,
                "distance": float(dist)
            })
        return results

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict]:
        """Mencari chunk berdasarkan chunk_id."""
        for chunk in self.metadata:
            if chunk['chunk_id'] == chunk_id:
                return chunk
        return None

    def get_all_chunk_ids(self) -> List[str]:
        """Mengembalikan daftar semua chunk_id yang ada."""
        return [c['chunk_id'] for c in self.metadata]

    def save(self, index_path: str, metadata_path: str) -> None:
        """Menyimpan indeks dan metadata ke disk."""
        faiss.write_index(self.index, index_path)
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        self.index_path = index_path
        self.metadata_path = metadata_path

    def load(self, index_path: str, metadata_path: str) -> None:
        """Memuat indeks dan metadata dari disk."""
        self.index = faiss.read_index(index_path)
        with open(metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)
        self.index_path = index_path
        self.metadata_path = metadata_path

    def clear(self) -> None:
        """Menghapus indeks dan metadata dari memori."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []