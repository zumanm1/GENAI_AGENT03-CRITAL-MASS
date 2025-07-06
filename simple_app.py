#!/usr/bin/env python3
"""
Simplified Flask Application for Network Automation AI Agent
This version uses minimal dependencies to ensure compatibility
"""

import os
import sys
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import datetime, timezone
import json
import requests
import uuid
from PyPDF2 import PdfReader
import pandas as pd
import io
import sqlite3

# ==============================================================================
# Logging and Application Setup
# ==============================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="src/web/templates", static_folder="src/web/static")
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
CORS(app)

# ==============================================================================
# Core Application Imports
# ==============================================================================
# Ensure the src directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from core.database import DatabaseManager
from core.models import User, Role
# ==============================================================================
# Database and Authentication Setup
# ==============================================================================
db_manager = DatabaseManager()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db_manager.get_user(user_id=int(user_id))
# In a real-world application, this would be replaced with a more persistent
# and scalable solution like a Redis cache, a database, or a dedicated
# vector store. The session_id from the client is used as the key.
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_manager.session.remove()


# ==============================================================================
# Frontend Rendering Routes
# ==============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db_manager.get_user(username=username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/')
@login_required
def index():
    stats = {
        "total_devices": db_manager.get_device_count(),
        "online_devices": db_manager.get_device_count(status='online'),
        "offline_devices": db_manager.get_device_count(status='offline'),
        "total_documents": db_manager.get_document_count(),
        "last_audit": db_manager.get_last_audit_timestamp()
    }
    devices = db_manager.get_all_devices()
    return render_template('dashboard.html', stats=stats, devices=devices)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """
    Renders the dashboard page. Serves as an alternative route to index().

    Returns:
        Rendered HTML template for the dashboard.
    """
    return index()

@app.route('/devices')
def devices():
    """
    Renders the device management page.

    Displays a list of all mock network devices and their current status.

    Returns:
        Rendered HTML template for the device list.
    """
    devices = db_manager.get_all_devices()
    return render_template('devices.html', devices=devices)

@app.route('/chat')
def chat():
    """
    Renders the main chat interface page.

    Generates a unique session ID for the user to ensure that their
    file uploads for RAG are isolated from other users.

    Returns:
        Rendered HTML template for the chat page, with a unique session_id.
    """
    session_id = str(uuid.uuid4())
    logger.info(f"New chat session created with ID: {session_id}")
    return render_template('chat.html', session_id=session_id)

@app.route('/documents')
def documents():
    """
    Renders the document management page.

    Displays a list of mock documents that could be managed by the system.
    Note: This is mock data and is not connected to the RAG uploads.

    Returns:
        Rendered HTML template for the documents page.
    """
    mock_documents = [
        {"id": 1, "filename": "Network_Config_Guide.pdf", "file_type": "pdf", "size": 2500000, "status": "processed", "uploaded_at": datetime(2024, 1, 10, 10, 30)},
        {"id": 2, "filename": "OSPF_Troubleshooting.docx", "file_type": "docx", "size": 1800000, "status": "processed", "uploaded_at": datetime(2024, 1, 12, 11, 0)},
        {"id": 3, "filename": "BGP_Best_Practices.pdf", "file_type": "pdf", "size": 3200000, "status": "error", "uploaded_at": datetime(2024, 1, 14, 15, 45)},
    ]
    return render_template('documents.html', documents=mock_documents)

@app.route('/audit')
def audit():
    """
    Renders the network audit page.

    Displays a list of mock devices and the results of recent mock audit tests.

    Returns:
        Rendered HTML template for the audit page.
    """
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
    """
    Renders the application settings page.

    Returns:
        Rendered HTML template for the settings page.
    """
    return render_template('settings.html')

# ==============================================================================
# API Routes
# ==============================================================================

@app.route('/api/health')
def health_check():
    """
    Provides a simple health check endpoint.

    This can be used by monitoring services to verify that the application
    is running and responsive.

    Returns:
        JSON object with the application's health status and version.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0-simplified'
    })

@app.route('/api/stats')
def get_stats():
    """
    API endpoint to get mock application statistics.

    Returns:
        JSON object containing the mock statistics data.
    """
    return jsonify(MOCK_STATS)

@app.route('/api/devices', methods=['GET'])
def api_get_devices():
    """
    API endpoint to get the list of all mock devices.

    Returns:
        JSON object containing a list of mock devices.
    """
    return jsonify(MOCK_DEVICES)

@app.route('/api/chat/message', methods=['POST'])
def api_chat_message():
    """
    Handles incoming chat messages from the user.

    This is the core endpoint for the AI chat functionality. It takes the user's
    message, combines it with any context from an uploaded file (RAG), sends
    it to the Ollama LLM, and returns the AI's response.

    Body:
        A JSON object containing:
        - content (str): The user's message.
        - model (str): The name of the Ollama model to use.
        - file_context_id (str, optional): The ID of the uploaded file context.

    Returns:
        JSON object with the AI's response or an error message.
    """
    try:
        data = request.get_json(silent=True)
        message = ""
        model = None
        file_context_id = None
        session_id = None
        if data:
            message = data.get('content', '').lower()
            model = data.get('model')
            file_context_id = data.get('file_context_id')
            session_id = data.get('session_id')

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

        # If a file context ID is provided, retrieve the text content from our
        # in-memory store and prepend it to the user's prompt.
        final_prompt = message
        if file_context_id and file_context_id in uploaded_file_contexts:
            context = uploaded_file_contexts[file_context_id]
            final_prompt = f"Using the following context, please answer the question.\\n\\n--- Context ---\\n{context}\\n--- End Context ---\\n\\nQuestion: {message}"
            logger.info("Used uploaded file context for RAG.")

        # Send the final prompt (with or without RAG context) to the Ollama service.
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

        # Persist the assistant's response.
        if session_id:
            save_message(session_id, 'assistant', ai_response)

        # Save the user's message to the chat history.
        if session_id:
            save_message(session_id, 'user', message)

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
    """
    Checks the status of the Ollama service.

    This is a mock implementation. In a real scenario, this endpoint would
    ping the Ollama service to verify its actual availability and which
    model is currently loaded.

    Returns:
        JSON object with the mock status of the Ollama service.
    """
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
    """
    Gets the list of available models from the Ollama service.

    It queries the Ollama `/api/tags` endpoint and transforms the response
    into the format expected by the application's frontend.

    Returns:
        JSON object containing a list of formatted models and the current model,
        or an error if the service is unavailable.
    """
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

        # Assume the first model in the list is the default/current one.
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
    """
    Extracts text content from various file types for the RAG pipeline.

    This function acts as a dispatcher, detecting the file extension and
    using the appropriate library (`PyPDF2` for PDF, `pandas` for CSV/XLSX)
    to parse the file and return its text content as a string.

    Args:
        file: A file object from the Flask request.

    Returns:
        A string containing the extracted text from the file.
    """
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
    """
    Handles file uploads for creating RAG context.

    This endpoint receives a file from the client, validates it, and then
    passes it to the `extract_text_from_file` function. The extracted text
    is stored in the `uploaded_file_contexts` dictionary, keyed by the
    user's session ID, making it available for future chat messages.

    Headers:
        X-Session-ID (str): The unique session ID for the user.

    Returns:
        JSON object indicating success or failure, and the file_id.
    """
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

        # Store the extracted content in our in-memory dictionary.
        # The key is the user's session ID, which we also use as the file_id.
        file_id = session_id 
        uploaded_file_contexts[file_id] = content
        
        logger.info(f"Uploaded file for session {session_id}, size: {len(content)} bytes.")
        
        return jsonify({"success": True, "file_id": file_id})
    except Exception as e:
        logger.error(f"Error reading or storing uploaded file: {e}")
        return jsonify({"success": False, "error": "Could not process file."}), 500
    
@app.route('/api/ollama/model', methods=['POST'])
def api_select_ollama_model():
    """
    Mock endpoint to handle model selection from the client.

    In a real application, this would store the user's model preference in
    their server-side session or a database. For this simplified version,
    it just logs the request and returns a success message.

    Body:
        A JSON object containing:
        - model (str): The name of the model the user selected.

    Returns:
        JSON object indicating success.
    """
    # This is a mock endpoint for now. In a real application, you would
    # store this preference in the user's session.
    data = request.get_json()
    model_name = data.get('model')
    logger.info(f"Client requested to switch to model: {model_name}")
    
    # You could add logic here to verify the model exists
    
    return jsonify({"success": True, "message": f"Model switched to {model_name}"})

@app.route('/api/network/discover', methods=['POST'])
def api_network_discover():
    """
    Mock endpoint for triggering a network discovery task.

    Returns:
        JSON object with a mock success message.
    """
    return jsonify({
        'status': 'success',
        'message': 'Network discovery completed (mock)',
        'devices_found': len(MOCK_DEVICES),
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/api/network/audit', methods=['POST'])
def api_network_audit():
    """
    Mock endpoint for triggering a network audit task.

    Returns:
        JSON object with a mock success message.
    """
    return jsonify({
        'status': 'success',
        'message': 'Network audit completed (mock)',
        'tests_run': 15,
        'passed': 12,
        'failed': 3,
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/api/chat/history/<session_id>', methods=['GET'])
def api_chat_history(session_id):
    """Returns all stored messages for the provided session ID."""
    try:
        return jsonify(get_history(session_id))
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        return jsonify([]), 500

@app.errorhandler(404)
def not_found(error):
    """
    Custom 404 error handler.

    Renders the generic error page with a 'Page not found' message.

    Args:
        error: The error object.

    Returns:
        A rendered error template and a 404 status code.
    """
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Custom 500 error handler.

    Renders the generic error page with an 'Internal server error' message.

    Args:
        error: The error object.

    Returns:
        A rendered error template and a 500 status code.
    """
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    # Entry point for running the application directly.
    # The debug=True flag enables auto-reloading on code changes and provides
    # a helpful debugger in the browser. This should be set to False in a
    # production environment.
    logger.info("Starting simplified Flask application...")
    logger.info("Access the application at: http://localhost:5003")
    logger.info("This is a simplified version - full features require additional setup")
    
    app.run(debug=True, host='0.0.0.0', port=5003) 