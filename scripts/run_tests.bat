@echo off
echo ========================================================
echo Running Automated Test Suite (Pytest)
echo ========================================================

call .venv\Scripts\activate.bat
python -m pytest tests -v
