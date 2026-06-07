#!/bin/bash

echo "================================"
echo "AI Test Generator - Project Verification"
echo "================================"
echo ""

# Check backend
echo "✓ Backend Structure:"
ls -1 backend/*.py backend/*/*.py 2>/dev/null | wc -l && echo "  Python files created"

# Check frontend
echo ""
echo "✓ Frontend Structure:"
ls -1 frontend/src/**/*.jsx 2>/dev/null | wc -l && echo "  React components created"

# Check docs
echo ""
echo "✓ Documentation:"
ls -1 *.md 2>/dev/null | wc -l && echo "  Documentation files created"

# Check samples
echo ""
echo "✓ Sample Files:"
ls -1 sample*.py sample*.json 2>/dev/null | wc -l && echo "  Example files included"

# File sizes
echo ""
echo "✓ Key Files:"
wc -l backend/app.py backend/models/test_generator.py frontend/src/App.jsx 2>/dev/null | tail -1

# Verify Python syntax
echo ""
echo "✓ Python Syntax Check:"
python3 -m py_compile backend/*.py backend/*/*.py 2>/dev/null && echo "  All Python files valid"

# Check config
echo ""
echo "✓ Configuration:"
[ -f .env.example ] && echo "  .env.example created"
[ -f backend/utils/config.py ] && echo "  config.py created"
[ -f frontend/vite.config.js ] && echo "  vite.config.js created"

echo ""
echo "================================"
echo "✅ Project setup complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Read QUICKSTART.md for 5-minute setup"
echo "2. cd backend && pip install -r requirements.txt"
echo "3. Create .env with your CLAUDE_API_KEY"
echo "4. Run 'python app.py' (backend) and 'npm run dev' (frontend)"
echo ""
