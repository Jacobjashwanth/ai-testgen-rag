import json
import os
from typing import List

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models.schemas import (Chunk, GenerationResponse, TestGenerationRequest,
                            TestResult, UploadResponse)
from models.test_generator import TestGenerator
from services.file_parser import FileParser
from services.rag_retriever import RAGRetriever
from utils.config import Config
from utils.logger import RequestLoggingMiddleware, logger
from utils.pii import detect_pii, scrub_code_for_llm
from utils.security import SecurityMiddleware

# Initialize
app = FastAPI(title="AI Test Generator RAG")
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
rag_retriever = RAGRetriever(Config.FAISS_INDEX_PATH)
test_generator = TestGenerator(Config.CLAUDE_API_KEY)

# ============ Endpoints ============

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a Python file or API spec and add to RAG index."""
    try:
        if file.size > Config.MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # PII Detection
        from utils.pii import detect_pii
        pii_result = detect_pii(content_str)
        if pii_result.has_pii:
            print(f"[WARN] {pii_result.summary} in {file.filename}")
        
        # Parse file
        from services.file_parser import FileParser as FP
        chunks_list = FP.parse(file.filename, content_str)
        
        if not chunks_list:
            raise HTTPException(status_code=400, detail="No parseable content found")
        
        # Convert to dict format for RAG retriever
        from services.file_parser import Chunk as ChunkClass
        chunks_objects = []
        for chunk in chunks_list:
            chunks_objects.append(chunk)
        
        # Add to index
        count = rag_retriever.add_chunks(chunks_objects)
        
        return UploadResponse(
            filename=file.filename,
            chunks_count=count,
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/generate-tests", response_model=GenerationResponse)
async def generate_tests(request: TestGenerationRequest):
    """Generate test cases based on query."""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if not request.test_types:
            raise HTTPException(status_code=400, detail="At least one test type required")
        
        # Retrieve relevant chunks
        top_k = request.top_k or Config.TOP_K_CHUNKS
        retrieved_chunks = rag_retriever.retrieve(request.query, top_k)
        
        if not retrieved_chunks:
            return GenerationResponse(
                tests=[],
                query=request.query,
                total_chunks_searched=0
            )
        
        # Generate tests
        test_results = test_generator.generate_tests(
            request.query,
            retrieved_chunks,
            request.test_types
        )
        
        # Format response
        tests = []
        for result in test_results:
            chunks_data = []
            for chunk in result['citations']:
                chunks_data.append(Chunk(
                    content=chunk.content,
                    source_file=chunk.source_file,
                    line_start=chunk.line_start,
                    line_end=chunk.line_end,
                    chunk_type=chunk.chunk_type,
                    name=chunk.name
                ))
            
            tests.append(TestResult(
                test_code=result['test_code'],
                test_type=result['test_type'],
                citations=chunks_data
            ))
        
        return GenerationResponse(
            tests=tests,
            query=request.query,
            total_chunks_searched=len(retrieved_chunks)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating tests: {str(e)}")

@app.get("/index-status")
async def index_status():
    """Get current index statistics."""
    return {
        "total_chunks": rag_retriever.index.ntotal if rag_retriever.index else 0,
        "embedding_dimension": rag_retriever.embeddings_service.embedding_dim,
        "model": rag_retriever.embeddings_service.model_name
    }

@app.post("/clear-index")
async def clear_index():
    """Clear all stored chunks and index."""
    try:
        rag_retriever.clear_index()
        return {"status": "success", "message": "Index cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing index: {str(e)}")

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
