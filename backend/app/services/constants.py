# Constants for Gemini and RAG System

# Gemini Chat Model
GEMINI_CHAT_MODEL = "gemini-2.5-flash"

# Gemini Embedding Model for Gemini API (1536-dim)
GEMINI_EMBEDDING_MODEL = "models/gemini-embedding-exp-03-07"
GEMINI_EMBEDDING_DIM = 1536

# Chunking strategies
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 256

# Retrieval parameters
N_RESULTS = 3
MINIMUM_SCORE = 0.5

# Generation parameters
GENERATION_TEMPERATURE = 0.4
MAX_OUTPUT_TOKENS = 1024
STOP_SEQUENCES = ["\n\n", "User:"] 