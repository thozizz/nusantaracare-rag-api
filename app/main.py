# app/main.py
import os
import uuid
import hashlib
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Muat .env dari root proyek (override=True agar menimpa environment yang ada)
load_dotenv(override=True)

from .schemas import AskRequest, AskResponse, HealthResponse, Citation
from .services import VectorStore, Embedder, LLMClient, RAGPipeline

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def secure_hash_log(text: str) -> str:
    """Menyamarkan input sensitif pengguna untuk logging aman (Privacy Hygiene)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]

# --- Global Variables (akan diinisialisasi saat startup) ---
vector_store = None
rag_pipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager: inisialisasi & cleanup.
    - Startup: load vector store dan inisialisasi pipeline.
    - Shutdown: cleanup jika diperlukan.
    """
    global vector_store, rag_pipeline
    logger.info("🚀 Memulai aplikasi NusantaraCare RAG API...")
    
    try:
        # 1. Inisialisasi Embedder & Vector Store
        embedder = Embedder()
        vector_store = VectorStore(embedder)
        index_path = os.getenv("FAISS_INDEX_PATH", "data/faiss_index/index.faiss")
        metadata_path = os.getenv("FAISS_METADATA_PATH", "data/faiss_index/metadata.pkl")
        
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            logger.error(f"Indeks FAISS tidak ditemukan di {index_path}. Jalankan build_index.py dulu!")
            raise FileNotFoundError("Indeks FAISS belum dibuat.")
        
        vector_store.load(index_path, metadata_path)
        logger.info(f"✅ Vector store berhasil dimuat: {len(vector_store.metadata)} chunk")
        
        # 2. Inisialisasi LLM Client
        llm_client = LLMClient(provider=os.getenv("LLM_PROVIDER", "groq"))
        logger.info(f"✅ LLM Client berhasil diinisialisasi: {llm_client.model}")
        
        # 3. Inisialisasi RAG Pipeline
        rag_pipeline = RAGPipeline(vector_store, llm_client)
        logger.info("✅ RAG Pipeline siap digunakan.")
        
    except Exception as e:
        logger.error(f"❌ Gagal inisialisasi: {e}")
        raise e
    
    yield  # Server berjalan di sini
    
    # Shutdown (jika ada cleanup)
    logger.info("🛑 Mematikan aplikasi...")
    vector_store = None
    rag_pipeline = None

# --- Inisialisasi FastAPI App ---
app = FastAPI(
    title="NusantaraCare RAG API",
    version="1.0.0",
    description="Layanan API untuk Grounded RAG berbasis dokumen internal NusantaraCare",
    lifespan=lifespan
)

# =====================================================
# ENDPOINT 1: Health Check
# =====================================================
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Endpoint untuk mengecek status komponen sistem."""
    global vector_store, rag_pipeline
    
    components = {}
    overall_status = "ok"
    
    # 1. Cek vector store
    try:
        if vector_store and len(vector_store.metadata) > 0:
            components["vector_store"] = "ok"
        else:
            components["vector_store"] = "empty_or_uninitialized"
            overall_status = "degraded"
    except Exception as e:
        components["vector_store"] = f"failed: {str(e)}"
        overall_status = "degraded"
    
    # 2. Cek embedding model (coba encode satu kata)
    try:
        if vector_store and vector_store.embedder:
            _ = vector_store.embedder.encode(["test"])  # quick test
            components["embedding_model"] = "ok"
        else:
            components["embedding_model"] = "uninitialized"
            overall_status = "degraded"
    except Exception as e:
        components["embedding_model"] = f"failed: {str(e)}"
        overall_status = "degraded"
    
    # 3. Cek LLM (hanya cek model name, tidak panggil API)
    if rag_pipeline:
        components["llm"] = f"ok (model: {rag_pipeline.llm.model})"
    else:
        components["llm"] = "uninitialized"
        overall_status = "degraded"
    
    return HealthResponse(
        status=overall_status,
        version=app.version,
        components=components
    )

# =====================================================
# ENDPOINT 2: Ask (Pertanyaan RAG)
# =====================================================
@app.post("/ask", response_model=AskResponse, tags=["RAG"])
async def ask_question(request: AskRequest):
    """
    Mengirim pertanyaan ke asisten RAG NusantaraCare.
    - Jawaban hanya berdasarkan dokumen internal yang aktif.
    - Menyertakan kutipan sumber (citation).
    - Menolak pertanyaan di luar cakupan.
    """
    global rag_pipeline
    
    # Privacy Hygiene: hash query untuk logging
    hashed_query = secure_hash_log(request.question)
    logger.info(f"[ASK] trace: pending | query_hash: {hashed_query} | mode: {request.mode}")
    
    if rag_pipeline is None:
        logger.error("RAG Pipeline belum siap.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "reason_code": "service_not_ready",
                "message": "Sistem RAG belum siap. Silakan coba lagi nanti."
            }
        )
    
    try:
        # Proses pertanyaan
        response = rag_pipeline.ask(request.question, mode=request.mode)
        
        # Log trace_id
        logger.info(f"[ASK] trace: {response.trace_id} | status: {response.reason_code} | confidence: {response.confidence_label}")
        
        return response
        
    except ConnectionError as e:
        # Gagal koneksi ke LLM / vector DB
        logger.error(f"Connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "reason_code": "connection_error",
                "message": "Layanan terkait sedang mengalami gangguan koneksi."
            }
        )
    except TimeoutError as e:
        # LLM timeout
        logger.error(f"Timeout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "reason_code": "llm_timeout",
                "message": "Layanan AI terlalu lama merespons. Silakan coba lagi."
            }
        )
    except ValueError as e:
        # Error validasi atau konfigurasi
        logger.error(f"Value error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "reason_code": "invalid_config",
                "message": str(e)
            }
        )
    except Exception as e:
        # Error tak terduga
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "reason_code": "internal_error",
                "message": "Terjadi kesalahan internal pada server."
            }
        )

# =====================================================
# Root Endpoint (Informasi)
# =====================================================
@app.get("/", tags=["System"])
async def root():
    return {
        "service": "NusantaraCare RAG API",
        "version": app.version,
        "docs": "/docs",
        "health": "/health"
    }

# =====================================================
# Custom Error Handler untuk Validasi Pydantic
# =====================================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": {
                "reason_code": "validation_error",
                "message": "Permintaan tidak valid. Periksa format input.",
                "errors": exc.errors()
            }
        }
    )