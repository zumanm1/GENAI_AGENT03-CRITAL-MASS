#!/bin/bash

# Set project root and other paths
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT=$( dirname "$SCRIPT_DIR" )

APP_DIR="$PROJECT_ROOT/GENAI_AGENT03-CRITAL-MASS"
VENV_PATH="$PROJECT_ROOT/venv"
# Fallback: look one level up for venv if not found
if [ ! -d "$VENV_PATH" ] && [ -d "$(dirname "$PROJECT_ROOT")/venv" ]; then
    VENV_PATH="$(dirname "$PROJECT_ROOT")/venv"
fi
LOG_DIR="$APP_DIR/data/logs"
GUNICORN_ERROR_LOG="$LOG_DIR/gunicorn.error.log"
GUNICORN_ACCESS_LOG="$LOG_DIR/gunicorn.access.log"

# Function to print a fancy header
print_header() {
    echo "================================"
    echo "🚀 Starting Network Automation AI Agent..."
    echo "📍 Working directory: $PROJECT_ROOT"
}

# Function to check for and activate virtual environment
activate_venv() {
    if [ -d "$VENV_PATH" ]; then
        echo "✅ Virtual environment active: $VENV_PATH"
        source "$VENV_PATH/bin/activate"
    else
        echo "❌ Error: Virtual environment not found at $VENV_PATH"
        exit 1
    fi
}

# Function to check if Ollama is running
check_ollama() {
    if ! pgrep -f "ollama" > /dev/null; then
        echo "⚠️ Warning: Ollama service does not appear to be running."
    else
        echo "✅ Ollama service is running"
    fi
}

# Function to free the port if already in use
free_port() {
    if lsof -i :5003 -t >/dev/null; then
        echo "⚠️ Port 5003 is busy. Attempting to free it..."
        lsof -ti :5003 | xargs kill -9
    fi
}

# Main script execution
print_header
free_port
activate_venv
check_ollama

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Navigate to the app directory
cd "$APP_DIR" || exit

# Start the Flask app using Gunicorn
echo "🌐 Starting Gunicorn on http://0.0.0.0:5003"
exec gunicorn --workers 3 \
         --bind 0.0.0.0:5003 \
         --log-level=debug \
         --access-logfile "$GUNICORN_ACCESS_LOG" \
         --error-logfile "$GUNICORN_ERROR_LOG" \
         "simple_app:app"

echo "================================" 