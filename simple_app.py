#!/usr/bin/env python3
"""
Simplified Flask Application for Network Automation AI Agent
This version uses minimal dependencies to ensure compatibility
"""

import os
import sys
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
import json
import requests
import uuid
from PyPDF2 import PdfReader
import pandas as pd
import io

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder="src/web/templates", static_folder="src/web/static")
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Enable CORS
CORS(app)

# In-memory storage for uploaded file contexts
# In a real-world app, you'd use a more persistent store like a database or filesystem
uploaded_file_contexts = {}

# Mock data for demonstration
MOCK_DEVICES = [
    {"id": 1, "name": "R15", "ip": "172.16.39.115", "type": "PE Router", "status": "online"},
    {"id": 2, "name": "R16", "ip": "172.16.39.116", "type": "PE Router", "status": "online"},
    {"id": 3, "name": "R17", "ip": "172.16.39.117", "type": "P Router", "status": "offline"},
    {"id": 4, "name": "R18", "ip": "172.16.39.118", "type": "RR Router", "status": "online"},
    {"id": 5, "name": "R19", "ip": "172.16.39.119", "type": "CE Router", "status": "online"},
    {"id": 6, "name": "R20", "ip": "172.16.39.120", "type": "CE Router", "status": "offline"},
]

MOCK_STATS = {
    "total_devices": 6,
    "online_devices": 4,
    "offline_devices": 2,
    "total_documents": 3,
    "last_audit": "2024-01-15 10:30:00"
}

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html', 
                         stats=MOCK_STATS,
                         devices=MOCK_DEVICES)

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return index()

@app.route('/devices')
def devices():
    """Device management page"""
    return render_template('devices.html', devices=MOCK_DEVICES)

@app.route('/chat')
def chat():
    """Chat interface page"""
    session_id = str(uuid.uuid4())
    logger.info(f"New chat session created with ID: {session_id}")
    return render_template('chat.html', session_id=session_id)

@app.route('/documents')
def documents():
    """Document management page"""
    mock_documents = [
        {"id": 1, "filename": "Network_Config_Guide.pdf", "file_type": "pdf", "size": 2500000, "status": "processed", "uploaded_at": datetime(2024, 1, 10, 10, 30)},
        {"id": 2, "filename": "OSPF_Troubleshooting.docx", "file_type": "docx", "size": 1800000, "status": "processed", "uploaded_at": datetime(2024, 1, 12, 11, 0)},
        {"id": 3, "filename": "BGP_Best_Practices.pdf", "file_type": "pdf", "size": 3200000, "status": "error", "uploaded_at": datetime(2024, 1, 14, 15, 45)},
    ]
    return render_template('documents.html', documents=mock_documents)

@app.route('/audit')
def audit():
    """Network audit page"""
    mock_audits = [
        {"id": 1, "device": "R15", "test": "OSPF Neighbors", "status": "PASS", "timestamp": "2024-01-15 10:30:00"},
        {"id": 2, "device": "R16", "test": "BGP Peers", "status": "PASS", "timestamp": "2024-01-15 10:31:00"},
        {"id": 3, "device": "R17", "test": "Interface Status", "status": "FAIL", "timestamp": "2024-01-15 10:32:00"},
        {"id": 4, "device": "R18", "test": "OSPF Neighbors", "status": "PASS", "timestamp": "2024-01-15 10:33:00"},
        {"id": 5, "device": "R19", "test": "Connectivity", "status": "PASS", "timestamp": "2024-01-15 10:34:00"},
    ]
    return render_template('audit.html', devices=MOCK_DEVICES, recent_audits=mock_audits)

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

# API Routes
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0-simplified'
    })

@app.route('/api/stats')
def get_stats():
    """Get application statistics"""
    return jsonify(MOCK_STATS)

@app.route('/api/devices', methods=['GET'])
def api_get_devices():
    """Get all devices"""
    return jsonify(MOCK_DEVICES)

@app.route('/api/chat/message', methods=['POST'])
def api_chat_message():
    """Handle chat messages by sending them to the Ollama service"""
    try:
        data = request.get_json(silent=True)
        message = ""
        model = None
        file_context_id = None
        if data:
            message = data.get('content', '').lower()
            model = data.get('model')
            file_context_id = data.get('file_context_id')

        if not message:
            return jsonify({'response': "It seems I didn't get a message. Please try asking your question again."})

        if not model:
            logger.warning("No model specified in chat request. Trying to fall back to the first available model.")
            try:
                ollama_models_response = requests.get('http://localhost:11434/api/tags')
                ollama_models_response.raise_for_status()
                models_data = ollama_models_response.json()
                if models_data.get('models'):
                    model = models_data['models'][0]['name']
                    logger.info(f"Falling back to model: {model}")
                else:
                    raise ValueError("No Ollama models found on the system.")
            except Exception as e:
                error_msg = f"Could not automatically select an Ollama model: {e}"
                logger.error(error_msg)
                return jsonify({'response': f"AI service error: {error_msg}"})

        # Prepend file context if it exists
        final_prompt = message
        if file_context_id and file_context_id in uploaded_file_contexts:
            context = uploaded_file_contexts[file_context_id]
            final_prompt = f"Using the following context, please answer the question.\n\n--- Context ---\n{context}\n--- End Context ---\n\nQuestion: {message}"
            logger.info("Used uploaded file context for RAG.")

        # Send the message to the Ollama service
        try:
            ollama_response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    "model": model,
                    "prompt": final_prompt,
                    "stream": False
                }
            )
            ollama_response.raise_for_status()  # Raise an exception for bad status codes
            response_data = ollama_response.json()
            ai_response = response_data.get('response', 'Sorry, I could not generate a response.')
        except requests.exceptions.RequestException as e:
            logger.error(f"Could not connect to Ollama service: {e}")
            ai_response = "I'm having trouble connecting to the AI service. Please ensure Ollama is running."

        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ollama/status')
def api_ollama_status():
    """Check the status of the Ollama service"""
    # This is a mock implementation. In a real scenario, you would
    # ping the Ollama service to check its actual status.
    is_online = True  # Assume it's online for this example
    model_name = "Llama 3.1"  # Mock model name

    if is_online:
        return jsonify({
            "status": "online",
            "model_name": model_name
        })
    else:
        return jsonify({
            "status": "offline",
            "model_name": None
        })

@app.route('/api/ollama/models', methods=['GET'])
def api_get_ollama_models():
    """Get the list of available Ollama models"""
    try:
        ollama_response = requests.get('http://localhost:11434/api/tags')
        ollama_response.raise_for_status()
        models_data = ollama_response.json()
        
        # Transform the data to the format expected by the frontend
        formatted_models = []
        for model in models_data.get('models', []):
            formatted_models.append({
                "name": model.get('name'),
                "size": f"{model.get('size', 0) / 1_000_000_000:.2f} GB",
                "speed": "Fast" # Mock data
            })

        # Assume the first model is the current one for now
        current_model = formatted_models[0]['name'] if formatted_models else 'N/A'
            
        return jsonify({
            "models": formatted_models,
            "current_model": current_model
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"Could not connect to Ollama service to get models: {e}")
        return jsonify({"error": "Could not connect to Ollama service."}), 503
    except Exception as e:
        logger.error(f"Error fetching Ollama models: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

def extract_text_from_file(file):
    """Extracts text content from various file types."""
    filename = file.filename
    content = ""
    logger.info(f"Starting text extraction for file: {filename}")
    if filename.endswith('.txt'):
        logger.info("Detected .txt file. Reading content directly.")
        content = file.read().decode('utf-8')
    elif filename.endswith('.pdf'):
        logger.info("Detected .pdf file. Starting PDF text extraction.")
        reader = PdfReader(file)
        num_pages = len(reader.pages)
        for i, page in enumerate(reader.pages):
            logger.info(f"Extracting text from PDF page {i + 1}/{num_pages}")
            content += page.extract_text()
    elif filename.endswith('.csv'):
        logger.info("Detected .csv file. Parsing with pandas.")
        df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
        content = df.to_string()
    elif filename.endswith('.xlsx'):
        logger.info("Detected .xlsx file. Parsing with pandas.")
        df = pd.read_excel(file)
        content = df.to_string()
    
    logger.info(f"Finished text extraction for {filename}. Extracted {len(content)} characters.")
    return content

@app.route('/api/chat/upload', methods=['POST'])
def api_chat_upload():
    """Handles text file uploads for RAG context."""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part in the request."}), 400
    
    file = request.files['file']
    session_id = request.headers.get('X-Session-ID')

    logger.info(f"Received file upload for session {session_id}: {file.filename}")

    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file."}), 400

    if not session_id:
        return jsonify({"success": False, "error": "No session ID provided."}), 400

    allowed_extensions = ['.txt', '.pdf', '.csv', '.xlsx']
    if not any(file.filename.endswith(ext) for ext in allowed_extensions):
        return jsonify({"success": False, "error": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"}), 400

    try:
        content = extract_text_from_file(file)
        
        if not content:
            return jsonify({"success": False, "error": "Could not extract text from file."}), 400

        # Store the content. Using session_id as the key.
        file_id = session_id 
        uploaded_file_contexts[file_id] = content
        
        logger.info(f"Uploaded file for session {session_id}, size: {len(content)} bytes.")
        
        return jsonify({"success": True, "file_id": file_id})
    except Exception as e:
        logger.error(f"Error reading or storing uploaded file: {e}")
        return jsonify({"success": False, "error": "Could not process file."}), 500
    
@app.route('/api/ollama/model', methods=['POST'])
def api_select_ollama_model():
    """Selects the Ollama model to use."""
    # This is a mock endpoint for now. In a real application, you would
    # store this preference in the user's session.
    data = request.get_json()
    model_name = data.get('model')
    logger.info(f"Client requested to switch to model: {model_name}")
    
    # You could add logic here to verify the model exists
    
    return jsonify({"success": True, "message": f"Model switched to {model_name}"})

@app.route('/api/network/discover', methods=['POST'])
def api_network_discover():
    """Mock network discovery"""
    return jsonify({
        'status': 'success',
        'message': 'Network discovery completed (mock)',
        'devices_found': len(MOCK_DEVICES),
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/api/network/audit', methods=['POST'])
def api_network_audit():
    """Mock network audit"""
    return jsonify({
        'status': 'success',
        'message': 'Network audit completed (mock)',
        'tests_run': 15,
        'passed': 12,
        'failed': 3,
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    logger.info("Starting simplified Flask application...")
    logger.info("Access the application at: http://localhost:5003")
    logger.info("This is a simplified version - full features require additional setup")
    
    app.run(debug=True, host='0.0.0.0', port=5003) 