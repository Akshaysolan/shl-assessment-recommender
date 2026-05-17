#!/bin/bash
set -e
# Load .env if present
[ -f .env ] && export $(grep -v '^#' .env | xargs)

if [ -z "$GROQ_API_KEY" ]; then
  echo "❌  GROQ_API_KEY is not set."
  echo "    Get a free key at https://console.groq.com"
  echo "    Then: export GROQ_API_KEY=gsk_..."
  exit 1
fi

echo "✅  GROQ_API_KEY found"
echo "🚀  Starting server → http://localhost:8000"
echo "📖  Swagger docs   → http://localhost:8000/docs"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
