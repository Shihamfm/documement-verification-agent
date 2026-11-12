#!/bin/bash
set -e

echo "========================================================"
echo "Starting Clinical Document Verification System (Backend + UI)"
echo "========================================================"

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

echo "Starting server on http://localhost:8000"
python3 main.py
