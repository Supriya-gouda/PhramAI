@echo off
cd /d "%~dp0\frontend"
echo Starting PharmAI Frontend...
streamlit run app.py --server.port=8501 --server.headless=true
pause
