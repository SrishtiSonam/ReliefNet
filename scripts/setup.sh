#!/bin/bash
# scripts/setup.sh - Complete setup script

set -e

echo "🚀 SDPDIAP System Setup"
echo "======================="

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup Python environment
echo "🐍 Setting up Python environment..."
cd ml_service

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

echo "✅ Python environment ready"

# Setup Node.js dependencies
echo "📦 Installing Node.js dependencies..."

cd ../backend
npm install

cd ../frontend  
npm install

echo "✅ Node.js dependencies installed"

# Generate synthetic data
echo "🎲 Generating synthetic data..."
cd ../ml_service
source .venv/bin/activate
python train/generate_synthetic_data.py

echo "✅ Synthetic data generated"

# Train initial models
echo "🧠 Training initial models..."
python train/train_dl_vfa.py
python train/train_nn_vfa.py --epochs 20

echo "✅ Models trained"

# Create necessary directories
echo "📁 Creating directories..."
cd ..
mkdir -p artifacts/experiments
mkdir -p logs
mkdir -p data/uploads

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Run: make run-ml     (Terminal 1)"  
echo "2. Run: make run-backend (Terminal 2)"
echo "3. Run: make run-frontend (Terminal 3)"
echo "4. Open: http://localhost:3000"
echo "5. Login: operator / demo123"

# scripts/demo.sh - Quick demo script
#!/bin/bash

echo "🎪 SDPDIAP Demo Script"
echo "===================="

# Start services in background
echo "🔄 Starting services..."

# Start ML service
cd ml_service
source .venv/bin/activate
nohup uvicorn main:app --reload --port 8000 > ../logs/ml_service.log 2>&1 &
ML_PID=$!
cd ..

sleep 3

# Start backend
cd backend  
nohup node server.js > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

sleep 2

# Start frontend
cd frontend
nohup npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "✅ Services started!"
echo "📊 ML Service: http://localhost:8000 (PID: $ML_PID)"
echo "🔧 Backend: http://localhost:4000 (PID: $BACKEND_PID)" 
echo "🖥️  Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"

echo ""
echo "💻 Demo ready! Opening browser..."
sleep 5

# Try to open browser (works on most systems)
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:3000
elif command -v open > /dev/null; then
    open http://localhost:3000
else
    echo "🌐 Please open http://localhost:3000 in your browser"
fi

echo ""
echo "🎮 Demo Instructions:"
echo "1. Login with: operator / demo123"
echo "2. Click 'Generate Recommendations'"
echo "3. View explanations and modify constraints"
echo "4. Accept recommendations"
echo "5. Try simulation experiments"

echo ""
echo "⏹️  To stop demo: kill $ML_PID $BACKEND_PID $FRONTEND_PID"

# Save PIDs for cleanup
echo "$ML_PID $BACKEND_PID $FRONTEND_PID" > .demo_pids

# scripts/stop_demo.sh - Stop demo script
#!/bin/bash

echo "⏹️  Stopping SDPDIAP demo..."

if [ -f .demo_pids ]; then
    PIDS=$(cat .demo_pids)
    for pid in $PIDS; do
        if kill -0 $pid 2>/dev/null; then
            echo "Stopping process $pid"
            kill $pid
        fi
    done
    rm .demo_pids
    echo "✅ Demo stopped"
else
    echo "❓ No demo PIDs found. Trying to kill by port..."
    
    # Kill processes on known ports
    lsof -ti:3000 | xargs -r kill
    lsof -ti:4000 | xargs -r kill  
    lsof -ti:8000 | xargs -r kill
    
    echo "✅ Port cleanup complete"
fi

# scripts/test_all.sh - Comprehensive test script
#!/bin/bash

echo "🧪 Running SDPDIAP test suite"
echo "============================"

EXIT_CODE=0

# Test ML service
echo "🔬 Testing ML service..."
cd ml_service
source .venv/bin/activate

if python -m pytest tests/ -v; then
    echo "✅ ML service tests passed"
else
    echo "❌ ML service tests failed"
    EXIT_CODE=1
fi

cd ..

# Test API endpoints (if services are running)
echo "🌐 Testing API endpoints..."

if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ ML service is responding"
    
    # Test forecast endpoint
    if curl -f -X POST -H "Content-Type: application/json" \
        -d '{"district_ids":["D001"],"horizon":6}' \
        http://localhost:8000/forecast/batch > /dev/null 2>&1; then
        echo "✅ Forecast endpoint working"
    else
        echo "❌ Forecast endpoint failed"
        EXIT_CODE=1
    fi
else
    echo "⚠️  ML service not running - skipping API tests"
fi

if curl -f http://localhost:4000/ > /dev/null 2>&1; then
    echo "✅ Backend service is responding"
else
    echo "⚠️  Backend service not running - skipping backend tests"
fi

# Test data integrity
echo "📊 Testing data integrity..."

if [ -f "data/scenarios/baseline.json" ]; then
    echo "✅ Scenario files exist"
else
    echo "❌ Scenario files missing"
    EXIT_CODE=1
fi

if [ -f "ml_service/models/dl_vfa.pkl" ]; then
    echo "✅ Trained models exist"
else
    echo "❌ Trained models missing"
    EXIT_CODE=1
fi

# Summary
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 All tests passed!"
else
    echo "💥 Some tests failed - check logs above"
fi

exit $EXIT_CODE

# Make scripts executable
chmod +x scripts/setup.sh
chmod +x scripts/demo.sh  
chmod +x scripts/stop_demo.sh
chmod +x scripts/test_all.sh