#!/bin/bash
set -e
[ -f .env ] && export $(grep -v '^#' .env | xargs)

if [ -z "$GROQ_API_KEY" ]; then
  echo "⚠️   No GROQ_API_KEY — running 16 unit tests only"
  python -m pytest tests/ -v -k "not Live and not Recall and not Behavior"
else
  echo "✅  GROQ_API_KEY set — running full suite (30 tests)"
  python -m pytest tests/ -v
fi
