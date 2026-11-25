#!/usr/bin/env bash
# ==============================================================================
# PodResearch 2.0 - Application Launcher
# Starts both FastAPI Backend (port 8000) and React Vite Frontend (port 3000)
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Ensure common paths for node/npm are in PATH
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

echo "=================================================="
echo "🎙️  Starting PodResearch 2.0"
echo "=================================================="

# 1. Locate Python Interpreter
PYTHON_CMD="python3"
if [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"
    echo "🐍 Using virtualenv Python: $PYTHON_CMD"
elif [ -f "$SCRIPT_DIR/../.venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/../.venv/bin/python"
    echo "🐍 Using parent virtualenv Python: $PYTHON_CMD"
elif [ -f "$BACKEND_DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$BACKEND_DIR/.venv/bin/python"
    echo "🐍 Using backend virtualenv Python: $PYTHON_CMD"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
    echo "🐍 Using system Python: $(which python3)"
else
    echo "❌ Error: Python 3 not found!"
    exit 1
fi

# 2. Check Node / npm
if ! command -v npm &>/dev/null; then
    echo "❌ Error: npm is not installed or not in PATH!"
    exit 1
fi
echo "📦 Using Node $(node -v) / npm $(npm -v)"

# 3. Ensure Backend .env exists
if [ ! -f "$BACKEND_DIR/.env" ]; then
    if [ -f "$SCRIPT_DIR/.env" ]; then
        echo "📋 Copying existing credentials from .env to backend/.env"
        cp "$SCRIPT_DIR/.env" "$BACKEND_DIR/.env"
    elif [ -f "$SCRIPT_DIR/../.env" ]; then
        echo "📋 Copying existing credentials from ../.env to backend/.env"
        cp "$SCRIPT_DIR/../.env" "$BACKEND_DIR/.env"
    elif [ -f "$BACKEND_DIR/.env.example" ]; then
        echo "📋 Initializing backend/.env from .env.example"
        cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
    fi
fi

# 4. Cleanup function for graceful shutdown on Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Shutting down PodResearch 2.0 servers..."
    if [ -n "${BACKEND_PID:-}" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "${FRONTEND_PID:-}" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    wait 2>/dev/null || true
    echo "👋 Shutdown complete."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# 5. Start Backend Server (FastAPI on Port 8000)
echo ""
echo "🚀 [1/2] Launching Backend on http://localhost:8000 ..."
(
    cd "$BACKEND_DIR"
    export PYTHONPATH="$BACKEND_DIR:${PYTHONPATH:-}"
    "$PYTHON_CMD" run.py
) &
BACKEND_PID=$!

# Wait briefly for backend to initialize
sleep 2

# 6. Start Frontend Server (Vite on Port 3000)
echo "✨ [2/2] Launching React Frontend on http://localhost:3000 ..."
(
    cd "$FRONTEND_DIR"
    npm run dev
) &
FRONTEND_PID=$!

echo ""
echo "=================================================="
echo "✅ PodResearch 2.0 is up and running!"
echo "   - 🌐 Frontend:  http://localhost:3000"
echo "   - 📖 API Docs:  http://localhost:8000/docs"
echo "   - ❤️  Health:    http://localhost:8000/api/health"
echo "=================================================="
echo "Press Ctrl+C to stop all servers."
echo ""

# Wait for both background processes
wait "$BACKEND_PID" "$FRONTEND_PID"
