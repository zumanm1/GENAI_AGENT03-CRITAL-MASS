#!/bin/bash

# Network Automation AI Agent - Startup Script (Local Modified Version)
# This script ensures proper Python path configuration and starts the Flask app

echo "🚀 Starting Network Automation AI Agent..."
echo "📍 Working directory: $(pwd)"

# Set environment variables
export PYTHONPATH="${PWD}:${PWD}/config"
export FLASK_ENV=development
export FLASK_DEBUG=1

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  Virtual environment not detected. Consider activating it."
fi

# Start the Flask application
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
echo "Press Ctrl+C to stop the server"
echo "================================"

cd "$(dirname "$0")"
source venv/bin/activate
python src/web/app.py
