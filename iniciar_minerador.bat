@echo off
echo Iniciando o Minerador de Contas (Local)
echo ========================================

:: Inicia o Backend Python em uma nova janela
echo Iniciando Backend (FastAPI)...
start "Backend - FastAPI" cmd /k "cd backend && venv\Scripts\activate && uvicorn src.main:app --reload --port 8000"

:: Inicia o Frontend React/Vite em uma nova janela
echo Iniciando Frontend (React/Vite)...
start "Frontend - Vite" cmd /k "cd frontend && npm run dev"

echo Tudo iniciado! 
echo O frontend deve abrir automaticamente ou acesse http://localhost:5173
pause
