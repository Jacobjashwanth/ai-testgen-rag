# Setup Guide: AI Test Case Generator

This guide walks you through setting up and running the AI Test Generator RAG application.

## Prerequisites

- **Python 3.9+** (tested with 3.10, 3.11, 3.12)
- **Node.js 18+** (for frontend)
- **npm** or **yarn**
- **Anthropic API Key** (get one at https://console.anthropic.com/)

## Step 1: Clone/Setup Project

```bash
cd /path/to/ai_testgen
```

## Step 2: Backend Setup

### 2.1 Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### 2.2 Configure API Key

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Anthropic API key
# CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxx
```

### 2.3 Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note**: If you encounter Python 3.14 compatibility issues with libexpat, use Python 3.12 or 3.11:

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2.4 Verify Installation

```bash
cd backend
python3 -c "import fastapi, anthropic, sentence_transformers, faiss; print('✓ All dependencies installed')"
```

### 2.5 Run Backend Server

```bash
# From backend directory
cd backend
python app.py
```

Server will start at `http://localhost:8000`

**Verify it's working:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

## Step 3: Frontend Setup

### 3.1 Install Dependencies

```bash
cd frontend
npm install
```

### 3.2 Run Development Server

```bash
npm run dev
```

Frontend will start at `http://localhost:5173`

## Step 4: Test the Application

### Using the Web UI

1. Open http://localhost:5173 in your browser
2. Upload `sample_auth.py` or `sample_api_spec.json`
3. Write a query: "Generate tests for user authentication"
4. Select test types (Pytest, REST, etc.)
5. Click "Generate Tests"

### Using curl/API directly

#### 1. Upload a file

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@../sample_auth.py"
```

Response:
```json
{
  "filename": "sample_auth.py",
  "chunks_count": 8,
  "status": "success"
}
```

#### 2. Generate tests

```bash
curl -X POST http://localhost:8000/generate-tests \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Generate pytest tests for the User class",
    "test_types": ["pytest"],
    "top_k": 5
  }'
```

#### 3. Check index status

```bash
curl http://localhost:8000/index-status
```

## Deployment Options

### Option 1: Docker Compose

```bash
# Build and run with docker-compose
docker-compose up --build

# Backend runs on port 8000
# Frontend runs on port 5173
```

### Option 2: Production with Nginx + Gunicorn

**Backend (Gunicorn):**
```bash
cd backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

**Frontend (Build & Serve):**
```bash
cd frontend
npm run build
# Serve dist/ with any web server (Nginx, Apache, etc.)
```

**Nginx Config Example:**
```nginx
upstream backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name example.com;
    
    # Frontend
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://backend/;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

## Troubleshooting

### Backend Issues

**Issue: "ModuleNotFoundError: No module named 'anthropic'"**
```bash
# Ensure virtual env is activated
source venv/bin/activate
pip install anthropic
```

**Issue: "CLAUDE_API_KEY not found"**
```bash
# Check .env file exists and has valid key
cat .env
# Should show: CLAUDE_API_KEY=sk-ant-...
```

**Issue: FAISS installation fails**
```bash
# FAISS has binary wheels, ensure pip is updated
pip install --upgrade pip
pip install faiss-cpu
```

### Frontend Issues

**Issue: "Cannot find module 'react'"**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Issue: CORS errors in browser console**
- Ensure backend is running on http://localhost:8000
- Check CORS middleware in `backend/app.py`

**Issue: Vite dev server not starting**
```bash
# Kill any process on port 5173
lsof -ti:5173 | xargs kill -9
npm run dev
```

### API Issues

**Issue: File upload fails with 413**
- File is larger than 10MB (configurable in `config.py`)
- Increase `MAX_UPLOAD_SIZE`

**Issue: "Invalid Python syntax"**
- Uploaded Python file has syntax errors
- Test file locally: `python3 -m py_compile yourfile.py`

**Issue: Empty test results**
- No chunks were retrieved from the index
- Try uploading more files
- Check query is descriptive enough

## Performance Tuning

### Embeddings

To use different embedding models, edit `backend/utils/config.py`:

```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Lightweight, fast
# Or
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # Higher quality, slower
```

### FAISS Index

- Default: `IndexFlatL2` (accurate but slower for large datasets)
- For millions of chunks, use:

```python
# In backend/services/rag_retriever.py
index = faiss.IndexIVFFlat(quantizer, dim, nlist=100)
```

### Claude Model

Edit `backend/utils/config.py`:

```python
MODEL_NAME = "claude-3-5-sonnet-20241022"  # Current (fast, capable)
# Or
MODEL_NAME = "claude-3-opus-20240229"      # More powerful but slower
```

## Next Steps

1. **Integrate with CI/CD**: Generate tests on code push
2. **Add to IDE**: VSCode extension for inline test generation
3. **Database**: Replace JSON metadata with PostgreSQL for persistence
4. **Multi-user**: Add authentication and per-user indexes
5. **Test Execution**: Run generated tests and show results in UI
6. **Custom Prompts**: Let users customize test generation templates

## Support

For issues:
1. Check logs: `tail -f backend.log`
2. Enable debug mode in `config.py`
3. Check Anthropic API status: https://status.anthropic.com/
4. Review rate limits: https://console.anthropic.com/account/usage

## Additional Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- Sentence Transformers: https://www.sbert.net/
- FAISS: https://github.com/facebookresearch/faiss
- Anthropic API: https://docs.anthropic.com/
- React Vite: https://vitejs.dev/guide/
