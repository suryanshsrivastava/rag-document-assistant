# Constants for RAG System

# ===========================================
# Local LLM Settings (LM Studio)
# ===========================================
# Model name is set via LMSTUDIO_MODEL env var
# Recommended: mistral-small-3.1-24b-instruct (Q4_K_M ~8GB)

# ===========================================
# Local Embedding Model Settings
# ===========================================
# Model is set via EMBEDDING_MODEL env var
# Default: all-MiniLM-L6-v2 (384-dim)
LOCAL_EMBEDDING_DIM = 384  # For all-MiniLM-L6-v2

# Legacy Gemini settings (if using cloud provider)
GEMINI_CHAT_MODEL = "gemini-2.5-flash"
GEMINI_EMBEDDING_MODEL = "models/gemini-embedding-exp-03-07"
GEMINI_EMBEDDING_DIM = 1536

# ===========================================
# Chunking strategies
# ===========================================
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 256

# ===========================================
# Retrieval parameters
# ===========================================
N_RESULTS = 5
MINIMUM_SCORE = 0.3  # Lower threshold for local embeddings

# ===========================================
# Generation parameters
# ===========================================
GENERATION_TEMPERATURE = 0.4
MAX_OUTPUT_TOKENS = 1024
STOP_SEQUENCES = ["\n\n", "User:"] 