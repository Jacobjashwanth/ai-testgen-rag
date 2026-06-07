import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
    FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "../../storage")
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    TOP_K_CHUNKS = 5
    CHUNK_OVERLAP = 100
    MODEL_NAME = "claude-3-5-sonnet-20241022"
