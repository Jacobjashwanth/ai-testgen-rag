from pydantic import BaseModel
from typing import Optional, List

class Chunk(BaseModel):
    content: str
    source_file: str
    line_start: int
    line_end: int
    chunk_type: str  # "function", "class", "method", etc.
    name: str

class TestGenerationRequest(BaseModel):
    query: str
    test_types: List[str]  # ["pytest", "selenium", "rest"]
    top_k: Optional[int] = 5

class TestResult(BaseModel):
    test_code: str
    test_type: str
    citations: List[Chunk]

class GenerationResponse(BaseModel):
    tests: List[TestResult]
    query: str
    total_chunks_searched: int

class UploadResponse(BaseModel):
    filename: str
    chunks_count: int
    status: str
