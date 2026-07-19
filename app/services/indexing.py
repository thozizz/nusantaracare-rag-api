import os
from .parser import parse_document
from .embedder import Embedder
from .vector_store import VectorStore

def build_vector_index(md_filepath: str, index_path: str, metadata_path: str) -> VectorStore:
    """
    Membangun indeks FAISS dari dokumen markdown.
    """
    # 1. Parsing dokumen
    doc_metadata, chunks = parse_document(md_filepath)
    print(f"Parsing selesai: {len(chunks)} chunk ditemukan.")

    # 2. Inisialisasi embedder dan vector store
    embedder = Embedder()
    vector_store = VectorStore(embedder)

    # 3. Tambahkan chunk
    vector_store.add_chunks(chunks)

    # 4. Simpan ke disk
    vector_store.save(index_path, metadata_path)
    print(f"Indeks berhasil disimpan di {index_path} dan metadata di {metadata_path}")
    
    return vector_store