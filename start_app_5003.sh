#!/bin/bash

# Network Automation AI Agent - Working Version Startup Script
# Runs on port 5003 with core functionality

echo "🚀 Starting Network Automation AI Agent (Working Version)..."
echo "📍 Working directory: $(pwd)"

# Set environment variables
export PYTHONPATH="/home/bootssd-2t/Documents/GEN_AI-AUTOMATION:/home/bootssd-2t/Documents/GEN_AI-AUTOMATION/config"
export FLASK_ENV=development
export FLASK_DEBUG=1

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  Virtual environment not detected. Consider activating it."
fi

# Stop any existing Flask processes
echo "🛑 Stopping any existing Flask processes..."
pkill -f "python.*app.*py" 2>/dev/null || true
sleep 2

# Start the working Flask application
echo "🌐 Starting Flask app on http://localhost:5003"
echo "📊 Dashboard: http://localhost:5003"
echo "💬 Chat: http://localhost:5003/chat"
echo "🔧 Devices: http://localhost:5003/devices"
echo "📄 Documents: http://localhost:5003/documents"
echo "🔍 Audit: http://localhost:5003/audit"
echo "⚙️  AI Model Settings: http://localhost:5003/settings"
echo "🔍 Health Check: http://localhost:5003/api/health"
echo "📈 Stats: http://localhost:5003/api/stats"
echo ""
echo "✨ NEW FEATURES:"
echo "🤖 AI Model Selection (Auto-selects fastest model)"
echo "🔄 Dynamic model switching in chat interface"
echo "📡 Real-time Ollama model detection"
echo "⚡ Performance-optimized recommendations"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"

cd /home/bootssd-2t/Documents/GEN_AI-AUTOMATION
python src/web/app.py 