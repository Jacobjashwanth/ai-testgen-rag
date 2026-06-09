# AI Test Case Generator with RAG

A powerful web application that leverages Retrieval Augmented Generation (RAG) with Claude AI to automatically generate comprehensive test cases from your source code and API specifications.

## Features

✨ **Smart Code Analysis**
- AST-based parsing of Python files (extracts functions, classes, methods)
- OpenAPI/Swagger spec parsing
- Semantic chunking for better context retrieval

🤖 **RAG-Powered Test Generation**
- Sentence-transformer embeddings (all-MiniLM-L6-v2)
- FAISS vector index for fast similarity search
- Claude 3.5 Sonnet for intelligent test generation

🧪 **Multiple Test Types**
- **Pytest**: Unit tests with fixtures and edge cases
- **Selenium**: UI automation tests with proper waits
- **REST**: API integration tests with various scenarios

📚 **Citation-Aware Generation**
- Every generated test includes source code citations
- Line numbers and file references
- Browse original code snippets in the UI

## Project Structure

```
ai_testgen/
├── backend/              # FastAPI server
│   ├── app.py           # Main application
│   ├── requirements.txt  # Python dependencies
│   ├── models/          # Data models & test generator
│   ├── services/        # Business logic
│   └── utils/           # Configuration
├── frontend/            # React + Vite UI
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API client
│   │   └── App.jsx      # Main app
│   ├── package.json
│   └── vite.config.js
└── storage/            # FAISS indexes & metadata (auto-created)
```

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Anthropic API key

### Backend Setup

1. **Create environment file:**
```bash
cp .env.example .env
# Edit .env and add your CLAUDE_API_KEY
```

2. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

3. **Run the server:**
```bash
python app.py
# Server runs at http://localhost:8000
```

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Run dev server:**
```bash
npm run dev
# UI runs at http://localhost:5173
```

## API Endpoints

### `POST /upload`
Upload Python files or API specifications.

**Request:**
```
multipart/form-data
- file: The file to upload (.py, .json, .yaml)
```

**Response:**
```json
{
  "filename": "example.py",
  "chunks_count": 5,
  "status": "success"
}
```

### `POST /generate-tests`
Generate test cases based on a query.

**Request:**
```json
{
  "query": "Generate tests for user authentication",
  "test_types": ["pytest", "selenium", "rest"],
  "top_k": 5
}
```

**Response:**
```json
{
  "tests": [
    {
      "test_type": "pytest",
      "test_code": "...",
      "citations": [
        {
          "content": "def login(...)",
          "source_file": "auth.py",
          "line_start": 10,
          "line_end": 20,
          "chunk_type": "function",
          "name": "login"
        }
      ]
    }
  ],
  "query": "Generate tests for user authentication",
  "total_chunks_searched": 5
}
```

### `GET /index-status`
Get index statistics.

**Response:**
```json
{
  "total_chunks": 42,
  "embedding_dimension": 384,
  "model": "all-MiniLM-L6-v2"
}
```

### `POST /clear-index`
Clear all stored chunks.

## Workflow

1. **Upload Files**: Upload Python files or API specs using the file upload interface
2. **Indexing**: Files are parsed, chunked, and embedded automatically
3. **Query**: Write a natural language query describing the tests you need
4. **Select Test Types**: Choose which test types to generate (Pytest, Selenium, REST)
5. **Generate**: Claude AI generates tests with source citations
6. **Review & Copy**: View generated tests with syntax highlighting and copy to clipboard

## Technology Stack

**Backend:**
- FastAPI - Modern web framework
- sentence-transformers - Embedding model
- FAISS - Vector similarity search
- Anthropic - Claude API
- Pydantic - Data validation

**Frontend:**
- React 18 - UI framework
- Vite - Build tool
- Tailwind CSS - Styling
- Axios - HTTP client
- react-syntax-highlighter - Code display

## Configuration

Edit `backend/utils/config.py`:

```python
CLAUDE_API_KEY = "your-api-key"
FAISS_INDEX_PATH = "./storage"  # Where indexes are stored
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Sentence-transformer model
TOP_K_CHUNKS = 5  # Default chunks to retrieve
MODEL_NAME = "claude-3-5-sonnet-20241022"  # Claude model version
```

## Example Usage

### 1. Upload a Python File

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@myapp.py"
```

### 2. Generate Tests

```bash
curl -X POST http://localhost:8000/generate-tests \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Test the calculate_total function with edge cases",
    "test_types": ["pytest"],
    "top_k": 5
  }'
```

## Performance Notes

- **Embedding**: ~10ms per chunk (all-MiniLM-L6-v2 is lightweight)
- **FAISS Search**: O(1) for indexed search with <100k chunks
- **Claude Generation**: ~3-5s per test type (API latency)
- **Total E2E**: ~5-10s for test generation from query

## Limitations

- Maximum file size: 10MB (configurable)
- Python syntax must be valid
- API specs should follow OpenAPI 3.0 format
- Claude API rate limits apply

## Future Enhancements

- [ ] Support for Java, JavaScript, Go source files
- [ ] Database persistence (PostgreSQL)
- [ ] Advanced filtering (by function name, complexity)
- [ ] Batch test generation
- [ ] Test execution environment
- [ ] Custom prompt engineering
- [ ] Support for Terraform, Docker test generation

## Troubleshooting

**Issue**: "Could not fetch index status"
- Ensure backend is running at http://localhost:8000
- Check CORS configuration in app.py

**Issue**: "Error: CLAUDE_API_KEY not found"
- Create `.env` file with valid Anthropic API key
- Restart backend server

**Issue**: "Invalid Python syntax"
- Ensure uploaded Python file is valid
- Check for encoding issues (use UTF-8)

**Issue**: Slow test generation
- Claude API may be rate-limited
- Check API usage in Anthropic dashboard

## License

MIT

## Contributing

Contributions welcome! Please feel free to submit pull requests.

## Support

For issues and questions, please open an issue on GitHub.
# ai-testgen-rag
🤖 AI Test Case Generator with RAG - FastAPI backend + React/Vite frontend. Generates Pytest, Selenium, and REST tests from source code using Claude AI and FAISS embeddings.
