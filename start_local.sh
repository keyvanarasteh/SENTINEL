#!/bin/bash

# ==========================================
# 🛡️ SENTINEL - LOCAL DEVELOPMENT STARTUP
# ==========================================

# Define Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Clear Terminal
clear

# Display Banner
echo -e "${PURPLE}"
echo "███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     "
echo "██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     "
echo "███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     "
echo "╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     "
echo "███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗"
echo "╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝"
echo -e "${CYAN}   Security • Intelligence • Data Extraction v2.1${NC}"
echo ""
echo -e "${BLUE}   S${NC}ENTINEL     ${BLUE}I${NC}NTELLIGENCE"
echo -e "${BLUE}   E${NC}XTRACTION   ${BLUE}N${NC}ODE"
echo -e "${BLUE}   N${NC}ETWORK      ${BLUE}E${NC}NGINE"
echo -e "${BLUE}   T${NC}ECHNOLOGY   ${BLUE}L${NC}OGIC"
echo ""

echo -e "${BLUE}ℹ️  System Initialization Sequence Initiated...${NC}"
echo ""

# 1. Backend Check
echo -n "🔍 Checking Backend Environment... "
if [ -d "backend/venv" ]; then
    echo -e "${GREEN}[OK]${NC}"
else
    echo -e "${RED}[MISSING]${NC}"
    echo "⚠️  Creating virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo -e "${GREEN}✅ Backend environment created.${NC}"
fi

# 2. Frontend Check
echo -n "🔍 Checking Frontend Dependencies... "
if [ -d "frontend/node_modules" ]; then
     echo -e "${GREEN}[OK]${NC}"
else
    echo -e "${RED}[MISSING]${NC}"
    echo "⚠️  Installing Node modules..."
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✅ Frontend dependencies installed.${NC}"
fi

echo ""
echo -e "${GREEN}🚀 Starting Services...${NC}"
echo "----------------------------------------"

# Start Backend
echo -e "${PURPLE}🐍 Launching Backend (FastAPI)...${NC}"
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8002 &
BACKEND_PID=$!
cd ..

# Wait for backend to initialize
sleep 2

# Start Frontend
echo -e "${CYAN}⚛️  Launching Frontend (Vite)...${NC}"
cd frontend
# Use npx vite directly to avoid path issues with npm run
npx vite --host --port 5173 &
FRONTEND_PID=$!
cd ..

echo ""
echo "----------------------------------------"
echo -e "${GREEN}✅ SYSTEMS ONLINE${NC}"
echo ""
echo -e "📍 Frontend: ${BLUE}http://localhost:5173${NC}"
echo -e "📍 Backend:  ${BLUE}http://localhost:8002${NC}"
echo -e "📍 API Docs: ${BLUE}http://localhost:8002/docs${NC}"
echo ""
echo "Press Ctrl+C to stop all services..."

# Trap Ctrl+C
trap "echo ''; echo -e '${RED}🛑 Shutting down services...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Wait
wait
