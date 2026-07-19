from app.services.indexing import build_vector_index

if __name__ == "__main__":
    md_file = "data/raw_docs/nusantaracare_panduan_operasional_internal_v2.md"
    index_file = "data/faiss_index/index.faiss"
    metadata_file = "data/faiss_index/metadata.pkl"
    
    # Pastikan folder data/faiss_index ada
    import os
    os.makedirs("data/faiss_index", exist_ok=True)
    
    vector_store = build_vector_index(md_file, index_file, metadata_file)
    print("Indexing selesai.")