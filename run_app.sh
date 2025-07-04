#!/bin/bash

# Network Automation AI Agent - Startup Script
# This script ensures proper Python path configuration and starts the Flask app

echo "🚀 Starting Network Automation AI Agent..."
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

# Check if Ollama is running
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✅ Ollama service is running"
else
    echo "⚠️  Ollama service not detected. Please start Ollama first."
fi

# Start the Flask application
echo "🌐 Starting Flask app on http://localhost:5003"
echo "📊 Dashboard: http://localhost:5003"
echo "🔍 Health Check: http://localhost:5003/api/health"
echo "📈 Stats: http://localhost:5003/api/stats"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"

cd /home/bootssd-2t/Documents/GEN_AI-AUTOMATION
python src/web/app.py 