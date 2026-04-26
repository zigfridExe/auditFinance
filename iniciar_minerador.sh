#!/bin/bash

echo "Iniciando o Minerador de Contas (Local)"
echo "========================================"

# Função para encontrar porta disponível
find_available_port() {
    local port=$1
    while lsof -i :$port >/dev/null 2>&1; do
        port=$((port + 1))
    done
    echo $port
}

# Encontra porta disponível para o backend (começa em 8000)
BACKEND_PORT=$(find_available_port 8000)
echo "🔍 Porta disponível encontrada para backend: $BACKEND_PORT"

# Encontra porta disponível para o frontend (começa em 5173)
FRONTEND_PORT=$(find_available_port 5173)
echo "🔍 Porta disponível encontrada para frontend: $FRONTEND_PORT"

# Inicia o Backend Python em background
echo "🚀 Iniciando Backend (FastAPI) na porta $BACKEND_PORT..."
cd backend

# Cria venv se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativa venv
source venv/bin/activate

# Instala dependências se necessário
if [ ! -f "venv/.installed" ]; then
    echo "📦 Instalando dependências Python..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Cria arquivo .env com as portas para o frontend ler
cat > ../frontend/.env.local << EOF
VITE_API_URL=http://localhost:$BACKEND_PORT
VITE_FRONTEND_PORT=$FRONTEND_PORT
EOF

# Inicia backend com a porta do frontend como variável de ambiente
FRONTEND_PORT=$FRONTEND_PORT uvicorn src.main:app --reload --port $BACKEND_PORT &
BACKEND_PID=$!

# Espera um pouco para o backend iniciar
sleep 3

# Inicia o Frontend React/Vite em background
echo "🚀 Iniciando Frontend (React/Vite) na porta $FRONTEND_PORT..."
cd ../frontend
npm run dev -- --port $FRONTEND_PORT --host &
FRONTEND_PID=$!

echo "✅ Tudo iniciado!"
echo "🔗 Backend: http://localhost:$BACKEND_PORT"
echo "🔗 Frontend: http://localhost:$FRONTEND_PORT"
echo "📝 API URL configurada: http://localhost:$BACKEND_PORT"
echo "🌐 Frontend rodando com host para permitir acesso externo"
echo ""
echo "⏹️  Para parar os serviços, pressione Ctrl+C"

# Espera pelos processos em background
trap "echo 'Parando serviços...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f frontend/.env.local; exit" INT
wait
