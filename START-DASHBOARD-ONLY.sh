#!/bin/bash

echo "========================================"
echo "Starting DDN AI Dashboard (Standalone)"
echo "========================================"
echo ""

echo "This will start ONLY the dashboard UI for testing."
echo "For full system, use COMPLETE-SETUP-WIZARD.sh"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[X] Node.js not found!"
    echo ""
    echo "Please install Node.js from: https://nodejs.org/"
    echo "Then run this script again."
    exit 1
fi

echo "[OK] Node.js found: $(node --version)"
echo ""

# Navigate to dashboard directory
cd implementation/dashboard-ui

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies (first time only)..."
    echo "This may take 2-3 minutes..."
    echo ""
    npm install
    if [ $? -ne 0 ]; then
        echo "[X] npm install failed!"
        exit 1
    fi
    echo ""
    echo "[OK] Dependencies installed!"
    echo ""
fi

# Check if .env exists, create if not
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env <<EOF
VITE_API_URL=http://localhost:5005
EOF
    echo "[OK] .env file created"
    echo ""
fi

echo "========================================"
echo "Starting Dashboard Development Server"
echo "========================================"
echo ""
echo "The dashboard will be available at:"
echo ""
echo "   http://localhost:5173"
echo ""
echo "Note: Port 5173 is Vite's default dev server port"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Start development server
npm run dev
