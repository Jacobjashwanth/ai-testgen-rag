# Architecture Overview

## System Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                      React + Vite Frontend                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ FileUpload | QueryInterface | TestResults | CitationViewer  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↕ (HTTP/JSON)                          │
└─────────────────────────────────────────────────────────────────────┘
                                  ↕
┌─────────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ POST /upload              POST /generate-tests              │  │
│  │ GET /index-status         POST /clear-index                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↕                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                   Services Layer                           │    │
│  │  ┌──────────────────────────────────────────────────────┐  │    │
│  │  │ FileParser (AST)  → Extract functions, classes      │  │    │
│  │  │ EmbeddingsService → sentence-transformers           │  │    │
│  │  │ RAG Retriever     → FAISS similarity search          │  │    │
│  │  │ TestGenerator     → Claude API test synthesis        │  │    │
│  │  └──────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────────┐
│                    Storage Layer                                     │
│  ┌─────────────────────┐  ┌──────────────────────────────────────┐ │
│  │  FAISS Index        │  │  JSON Metadata                       │ │
│  │  (Vector DB)        │  │  (Chunk references & citations)      │ │
│  │  storage/           │  │  storage/chunks_metadata.json        │ │
│  │  faiss_index.bin    │  │                                      │ │
│  └─────────────────────┘  └──────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────────┐
│                  External APIs                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Anthropic Claude API (gpt-3-5-sonnet-20241022)            │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Upload & Indexing Flow

```
User uploads file (.py or .json)
         ↓
FileParser extracts chunks (AST for Python, OpenAPI for JSON)
         ↓
Each chunk contains:
  - content (source code)
  - source_file (filename)
  - line_start, line_end
  - chunk_type (function, class, method, endpoint)
  - name (function/class name)
         ↓
EmbeddingsService converts each chunk to 384-dim vector
         ↓
Vectors added to FAISS IndexFlatL2
         ↓
Chunk metadata stored in chunks_metadata.json
         ↓
Response: { filename, chunks_count, status }
```

### Test Generation Flow

```
User submits query: "Generate tests for user authentication"
         ↓
Query embedded using same model (all-MiniLM-L6-v2)
         ↓
FAISS searches for top-5 most similar chunks (L2 distance)
         ↓
Retrieved chunks formatted with context and file info
         ↓
For each selected test_type (pytest, selenium, rest):
  - Generate system prompt (test-type specific)
  - Combine with chunk context
  - Send to Claude API
  - Get back test code
         ↓
Response includes:
  - test_code (generated code)
  - citations (original chunks used)
  - similarity scores
         ↓
Frontend displays:
  - Syntax-highlighted test code
  - Copy button
  - Expandable citations with original source
```

## Component Details

### FileParser
- **Python Files**: Uses `ast` module to extract functions, classes, methods
- **API Specs**: Parses OpenAPI 3.0 JSON/YAML specs
- **Chunking Strategy**: One chunk per function/class/endpoint
- **Preserves**: Line numbers, file references for citations

### EmbeddingsService
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384D vectors
- **Speed**: ~10ms per chunk on CPU
- **Memory**: ~1.5GB for 100k chunks

### RAGRetriever
- **Index Type**: FAISS IndexFlatL2 (exact nearest neighbor)
- **Similarity Metric**: L2 distance → converted to 0-1 similarity
- **Scalability**: Suitable for up to 1M chunks
- **Persistence**: Binary index + JSON metadata

### TestGenerator
- **LLM**: Claude 3.5 Sonnet
- **Prompts**: Customized for each test type
- **Context**: Top-k chunks + file info
- **Output**: Runnable test code with docstrings

## Key Design Decisions

1. **Chunk Level**: Function/class instead of lines
   - More meaningful context for test generation
   - Cleaner citations
   - Better semantic boundaries

2. **Embeddings Model**: all-MiniLM-L6-v2 (not BERT-large)
   - Fast inference (10x faster than large models)
   - Good enough for code semantics
   - Reduced memory footprint
   - Suitable for CPU deployment

3. **FAISS IndexFlatL2**: Simple exact search
   - Accurate results
   - No false negatives
   - Linear time O(n) but acceptable for dev
   - Can upgrade to IndexIVFFlat for millions of chunks

4. **JSON Metadata Storage**: Instead of database
   - Simpler setup (no PostgreSQL required)
   - Easier to debug and inspect
   - Sufficient for development
   - Can migrate to DB later

5. **Per-Test-Type Prompts**: Customized generation
   - Pytest: Unit tests with fixtures
   - Selenium: UI tests with waits
   - REST: API integration tests
   - Better quality than generic prompts

## Scalability Considerations

### Vertical Scaling
- **Current**: Single machine, <100k chunks
- **Bottleneck**: Claude API rate limits (not FAISS)

### Horizontal Scaling
- **Multiple backends**: Load balance via Nginx
- **Shared storage**: Move storage to S3/GCS
- **Database**: PostgreSQL + pgvector for metadata
- **Message queue**: Redis for async test generation

### Performance Optimizations
- Batch embedding: Process files in parallel
- Query caching: Cache popular queries
- Incremental indexing: Only reindex changed files
- Model quantization: INT8 FAISS for memory efficiency

## Security Considerations

1. **API Key Protection**: Use environment variables, never commit keys
2. **File Upload**: Validate file types, enforce size limits
3. **Code Injection**: Sanitize Claude prompts
4. **Rate Limiting**: Implement request throttling
5. **CORS**: Restrict to trusted origins in production

## Monitoring & Logging

Add to production:
```python
import logging
logger = logging.getLogger("testgen")
logger.info(f"Retrieved {len(results)} chunks")
logger.warning(f"Slow query: {query_time}s")
```

Track:
- Query latency (embedding + search + generation)
- Cache hit rate
- API token usage
- Error rates
