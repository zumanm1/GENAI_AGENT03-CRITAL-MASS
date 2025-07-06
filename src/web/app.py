"""
Main Flask Application
Network Automation AI Agent Web Interface
"""

import logging
import os
import sys
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
import uuid

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.config import config
from core.database import db_manager
from core.ollama_service import ollama_service
from core.chromadb_service import chromadb_service
from rag.document_processor import document_processor

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.flask['SECRET_KEY']
app.config['MAX_CONTENT_LENGTH'] = config.upload['MAX_FILE_SIZE']

# Enable CORS
CORS(app, origins=config.api['CORS_ORIGINS'])

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    """Main dashboard page"""
    try:
        # Get basic stats
        stats = db_manager.get_stats()
        
        # Get recent devices
        devices = db_manager.get_all_devices()
        
        # Get recent audit results
        recent_audits = db_manager.get_latest_audit_results(limit=5)
        
        return render_template('dashboard.html', 
                             stats=stats,
                             devices=devices,
                             recent_audits=recent_audits)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/chat')
def chat():
    """Chat interface page"""
    # Generate session ID if not exists
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    return render_template('chat.html', session_id=session['session_id'])


@app.route('/devices')
def devices():
    """Device management page"""
    try:
        devices = db_manager.get_all_devices()
        return render_template('devices.html', devices=devices)
    except Exception as e:
        logger.error(f"Error loading devices: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/config-retrieve')
def config_retrieve():
    """Configuration retrieve placeholder page"""
    return render_template('config_retrieve.html')


@app.route('/config-push')
def config_push():
    """Configuration push placeholder page"""
    return render_template('config_push.html')


@app.route('/documents')
def documents():
    """Document management page"""
    try:
        documents = db_manager.get_all_documents()
        return render_template('documents.html', documents=documents)
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/dashboard')
def dashboard():
    """Dashboard page (same as index)"""
    print("Dashboard route called!")
    return index()


@app.route('/audit')
def audit():
    """Network audit page"""
    try:
        devices = db_manager.get_all_devices()
        recent_audits = db_manager.get_latest_audit_results(limit=10)
        return render_template('audit.html', devices=devices, recent_audits=recent_audits)
    except Exception as e:
        logger.error(f"Error loading audit page: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/settings')
def settings():
    """Settings page"""
    try:
        # Get available models
        models = ollama_service.list_models()
        current_model = config.ollama['MODEL_NAME']
        
        return render_template('settings.html', 
                             models=models, 
                             current_model=current_model)
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return render_template('error.html', error=str(e)), 500


# API Routes
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        db_health = db_manager.health_check()
        return jsonify({
            'status': 'healthy' if db_health else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected' if db_health else 'disconnected'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/stats')
def get_stats():
    """Get application statistics"""
    try:
        stats = db_manager.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/devices', methods=['GET'])
def api_get_devices():
    """Get all devices"""
    try:
        devices = db_manager.get_all_devices()
        return jsonify([device.to_dict() for device in devices])
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/devices', methods=['POST'])
def api_create_device():
    """Create a new device"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        device = db_manager.create_device(data)
        return jsonify(device.to_dict()), 201
    except Exception as e:
        logger.error(f"Error creating device: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/devices/<int:device_id>', methods=['GET'])
def api_get_device(device_id):
    """Get device by ID"""
    try:
        device = db_manager.get_device(device_id)
        if device:
            return jsonify(device.to_dict())
        return jsonify({'error': 'Device not found'}), 404
    except Exception as e:
        logger.error(f"Error getting device: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/devices/<int:device_id>', methods=['PUT'])
def api_update_device(device_id):
    """Update device"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        device = db_manager.update_device(device_id, data)
        if device:
            return jsonify(device.to_dict())
        return jsonify({'error': 'Device not found'}), 404
    except Exception as e:
        logger.error(f"Error updating device: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
def api_delete_device(device_id):
    """Delete device"""
    try:
        success = db_manager.delete_device(device_id)
        if success:
            return jsonify({'message': 'Device deleted successfully'})
        return jsonify({'error': 'Device not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting device: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/message', methods=['POST'])
def api_chat_message():
    """Send chat message"""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Message content required'}), 400
        
        session_id = data.get('session_id', session.get('session_id', str(uuid.uuid4())))
        
        # Save user message
        user_message = db_manager.create_chat_message({
            'session_id': session_id,
            'message_type': 'user',
            'content': data['content']
        })
        
        # Process message with AI agent
        messages = [
            {"role": "system", "content": "You are a helpful network automation AI assistant. Help users with network configuration, troubleshooting, and automation tasks. Be concise but informative."},
            {"role": "user", "content": data['content']}
        ]
        
        ai_result = ollama_service.chat_completion(messages, temperature=0.7, max_tokens=500)
        
        if ai_result['success']:
            response_content = ai_result['response']
        else:
            response_content = f"I'm sorry, I'm having trouble processing your request right now. Error: {ai_result.get('error', 'Unknown error')}"
        
        # Save assistant response
        assistant_message = db_manager.create_chat_message({
            'session_id': session_id,
            'message_type': 'assistant',
            'content': response_content,
            'agent_name': 'NetworkAgent',
            'agent_role': 'Network Assistant'
        })
        
        return jsonify({
            'session_id': session_id,
            'response': response_content,
            'message_id': assistant_message.id if assistant_message else None
        })
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/history/<session_id>')
def api_chat_history(session_id):
    """Get chat history for session"""
    try:
        messages = db_manager.get_chat_messages(session_id)
        return jsonify([message.to_dict() for message in reversed(messages)])
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/network/discover', methods=['POST'])
def api_network_discover():
    """Trigger network discovery"""
    try:
        # TODO: Implement network discovery
        # For now, return mock response
        return jsonify({
            'status': 'started',
            'message': 'Network discovery not yet implemented',
            'discovered_devices': []
        })
    except Exception as e:
        logger.error(f"Error starting network discovery: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/network/audit', methods=['POST'])
def api_network_audit():
    """Run network audit"""
    try:
        data = request.get_json()
        device_names = data.get('device_names', [])
        audit_types = data.get('audit_types', ['ping'])
        
        # TODO: Implement network audit
        # For now, return mock response
        return jsonify({
            'status': 'started',
            'message': 'Network audit not yet implemented',
            'audit_id': str(uuid.uuid4()),
            'devices': device_names,
            'audit_types': audit_types
        })
    except Exception as e:
        logger.error(f"Error starting network audit: {e}")
        return jsonify({'error': str(e)}), 500


# Ollama/AI API endpoints
@app.route('/api/ollama/health')
def api_ollama_health():
    """Check Ollama service health"""
    try:
        health_status = ollama_service.health_check()
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
    except Exception as e:
        logger.error(f"Error checking Ollama health: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ollama/models')
def api_ollama_models():
    """Get available Ollama models"""
    try:
        models = ollama_service.list_models()
        return jsonify({
            'models': models,
            'current_model': ollama_service.model,
            'count': len(models)
        })
    except Exception as e:
        logger.error(f"Error listing Ollama models: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/analyze-config', methods=['POST'])
def api_analyze_config():
    """Analyze network configuration using AI"""
    try:
        data = request.get_json()
        if not data or 'config_text' not in data:
            return jsonify({'error': 'Configuration text required'}), 400
        
        config_text = data['config_text']
        device_name = data.get('device_name', 'Unknown')
        
        # Analyze with Ollama
        result = ollama_service.analyze_network_config(config_text)
        
        if result['success']:
            # Save analysis result to database (optional)
            analysis_data = {
                'device_name': device_name,
                'analysis_type': 'config_analysis',
                'input_text': config_text[:500],  # Truncate for storage
                'ai_response': result['response'],
                'model_used': result['model'],
                'tokens_used': result.get('completion_tokens', 0),
                'timestamp': result['timestamp']
            }
            
            return jsonify({
                'success': True,
                'analysis': result['response'],
                'model': result['model'],
                'tokens_used': result.get('completion_tokens', 0),
                'device_name': device_name
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Analysis failed')
            }), 500
            
    except Exception as e:
        logger.error(f"Error analyzing config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/generate-commands', methods=['POST'])
def api_generate_commands():
    """Generate network commands using AI"""
    try:
        data = request.get_json()
        if not data or 'task_description' not in data:
            return jsonify({'error': 'Task description required'}), 400
        
        task_description = data['task_description']
        device_type = data.get('device_type', 'cisco_ios')
        
        # Generate commands with Ollama
        result = ollama_service.generate_network_command(task_description, device_type)
        
        if result['success']:
            return jsonify({
                'success': True,
                'commands': result['response'],
                'model': result['model'],
                'task_description': task_description,
                'device_type': device_type,
                'tokens_used': result.get('completion_tokens', 0)
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Command generation failed')
            }), 500
            
    except Exception as e:
        logger.error(f"Error generating commands: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/troubleshoot', methods=['POST'])
def api_troubleshoot():
    """Get AI-powered troubleshooting assistance"""
    try:
        data = request.get_json()
        if not data or 'issue_description' not in data:
            return jsonify({'error': 'Issue description required'}), 400
        
        issue_description = data['issue_description']
        device_logs = data.get('device_logs', '')
        
        # Get troubleshooting guidance with Ollama
        result = ollama_service.troubleshoot_network_issue(issue_description, device_logs)
        
        if result['success']:
            return jsonify({
                'success': True,
                'guidance': result['response'],
                'model': result['model'],
                'issue_description': issue_description,
                'tokens_used': result.get('completion_tokens', 0)
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Troubleshooting failed')
            }), 500
            
    except Exception as e:
        logger.error(f"Error in troubleshooting: {e}")
        return jsonify({'error': str(e)}), 500


# ChromaDB/Vector Database API endpoints
@app.route('/api/chromadb/health')
def api_chromadb_health():
    """Check ChromaDB service health"""
    try:
        health_status = chromadb_service.health_check()
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
    except Exception as e:
        logger.error(f"Error checking ChromaDB health: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/documents/add', methods=['POST'])
def api_add_document():
    """Add a document to the vector database"""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Document content required'}), 400
        
        document_id = data.get('id', str(uuid.uuid4()))
        content = data['content']
        metadata = data.get('metadata', {})
        
        # Add document type if not specified
        if 'type' not in metadata:
            metadata['type'] = 'network_document'
        
        success = chromadb_service.add_document(document_id, content, metadata)
        
        if success:
            return jsonify({
                'success': True,
                'document_id': document_id,
                'message': 'Document added successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add document'
            }), 500
            
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/documents/search', methods=['POST'])
def api_search_documents():
    """Search for similar documents"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Search query required'}), 400
        
        query = data['query']
        n_results = data.get('n_results', 5)
        filter_metadata = data.get('filter', None)
        
        results = chromadb_service.search_documents(query, n_results, filter_metadata)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rag/query', methods=['POST'])
def api_rag_query():
    """Query using RAG (Retrieval-Augmented Generation)"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query required'}), 400
        
        query = data['query']
        n_results = data.get('n_results', 3)
        
        # Search for relevant documents
        search_results = chromadb_service.search_documents(query, n_results)
        
        if not search_results:
            # No relevant documents found, use basic AI response
            messages = [
                {"role": "system", "content": "You are a helpful network automation AI assistant."},
                {"role": "user", "content": query}
            ]
        else:
            # Build context from search results
            context = "\n\n".join([f"Document: {result['content'][:500]}..." for result in search_results])
            
            messages = [
                {"role": "system", "content": f"You are a helpful network automation AI assistant. Use the following context to answer questions:\n\nContext:\n{context}"},
                {"role": "user", "content": query}
            ]
        
        # Get AI response with context
        ai_result = ollama_service.chat_completion(messages, temperature=0.7, max_tokens=500)
        
        if ai_result['success']:
            return jsonify({
                'success': True,
                'query': query,
                'response': ai_result['response'],
                'context_documents': len(search_results),
                'context_used': search_results[:3] if search_results else [],
                'model': ai_result['model']
            })
        else:
            return jsonify({
                'success': False,
                'error': ai_result.get('error', 'AI processing failed')
            }), 500
            
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/documents/upload', methods=['POST'])
def api_upload_document():
    """Upload and process document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file temporarily
        filename = file.filename
        temp_path = os.path.join('data', 'documents', filename)
        file.save(temp_path)
        
        # Process the document
        success = document_processor.process_file(temp_path)
        
        if success:
            return jsonify({
                'message': 'Document processed successfully',
                'filename': filename
            })
        else:
            return jsonify({'error': 'Failed to process document'}), 500
            
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', 
                         error="Page not found", 
                         error_code=404), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return render_template('error.html', 
                         error="Internal server error", 
                         error_code=500), 500


def initialize_default_devices():
    """Initialize default devices from configuration"""
    try:
        logger.info("Initializing default devices...")
        
        # Get configured devices
        configured_devices = config.get_network_devices()
        
        for device_name, device_config in configured_devices.items():
            # Check if device already exists
            existing_device = db_manager.get_device_by_name(device_name)
            if not existing_device:
                # Create new device
                device_data = {
                    'name': device_name,
                    'host': device_config['host'],
                    'device_type': device_config['device_type'],
                    'username': device_config['username'],
                    'password': device_config['password'],
                    'secret': device_config['secret'],
                    'role': device_config['role'],
                    'as_number': device_config['as_number'],
                    'status': 'unknown',
                    'vendor': 'Cisco',
                }
                
                device = db_manager.create_device(device_data)
                logger.info(f"Created device: {device_name}")
            else:
                logger.info(f"Device already exists: {device_name}")
                
    except Exception as e:
        logger.error(f"Error initializing default devices: {e}")


if __name__ == '__main__':
    logger.info("Starting Network Automation AI Agent...")
    
    # Initialize default devices if needed
    initialize_default_devices()
    
    app.run(
        host=config.flask.get('HOST', '0.0.0.0'),
        port=config.flask.get('PORT', 5003),
        debug=True
    ) 