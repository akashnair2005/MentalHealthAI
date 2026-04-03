@echo off
echo ==============================================
echo MindGuardian AI - Startup Script
echo ==============================================

IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r backend\requirements.txt

echo.
echo ==============================================
echo Starting FastAPI Backend...
echo ==============================================
echo.
echo Make sure you have created a .env file with GEMINI_API_KEY=your_key if you want real AI responses.
echo Otherwise, mock responses will be used.
echo.
echo Open 'frontend\index.html' in your browser to start chatting!
echo ==============================================
echo.

uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
