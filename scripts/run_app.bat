@echo off
echo ========================================================
echo Starting Clinical Document Verification System (Backend + UI)
echo ========================================================

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt

echo Starting server on http://localhost:8000
python main.py
