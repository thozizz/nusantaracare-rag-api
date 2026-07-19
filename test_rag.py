import os
from dotenv import load_dotenv
load_dotenv(override=True)

from app.services import VectorStore, Embedder, LLMClient, RAGPipeline

# Load vector store yang sudah dibuat
embedder = Embedder()
vector_store = VectorStore(embedder)
vector_store.load("data/faiss_index/index.faiss", "data/faiss_index/metadata.pkl")

# Inisialisasi LLM - HAPUS hardcode model_name
llm = LLMClient(provider="groq")  # <- model_name akan otomatis membaca .env

# Inisialisasi RAG Pipeline
rag = RAGPipeline(vector_store, llm)

# Uji pertanyaan
questions = [
    "Bagaimana cara mengajukan permintaan akses aplikasi?",
    "Berapa lama batas waktu pengakuan tiket P1?",
    "Apa saja data yang dilarang dalam tiket Service Portal?",
    "Siapa nama direktur utama NusantaraCare?",  # Seharusnya tidak ditemukan
]

for q in questions:
    print(f"\n{'='*60}")
    print(f"Pertanyaan: {q}")
    response = rag.ask(q)
    print(f"Answer: {response.answer}")
    print(f"Citations: {[(c.chunk_id, c.section_title) for c in response.citations]}")
    print(f"Confidence: {response.confidence_label}")
    print(f"Reason: {response.reason_code}")