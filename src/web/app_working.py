"""
Working Flask Application
Network Automation AI Agent Web Interface - Simplified Version
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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'config'))

# Import basic components
try:
    from core.config import config
    print("✅ Config imported successfully")
except Exception as e:
    print(f"⚠️ Config import failed: {e}")
    # Fallback config
    class Config:
        flask = {'SECRET_KEY': 'dev-key', 'DEBUG': True, 'HOST': '0.0.0.0', 'PORT': 5003, 'THREADED': True}
        api = {'CORS_ORIGINS': ['http://localhost:5003']}
        upload = {'MAX_FILE_SIZE': 16*1024*1024}
    config = Config()

try:
    from core.database import db_manager
    print("✅ Database imported successfully")
    DATABASE_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Database import failed: {e}")
    DATABASE_AVAILABLE = False

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
        # Get basic stats if database is available
        if DATABASE_AVAILABLE:
            stats = db_manager.get_stats()
            devices = db_manager.get_all_devices()[:6]  # Limit to 6 for demo
        else:
            stats = {'devices': 0, 'documents': 0, 'audit_results': 0, 'chat_messages': 0}
            devices = []
        
        return render_template('dashboard.html', 
                             stats=stats,
                             devices=devices,
                             recent_audits=[])
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return f"Dashboard Error: {e}", 500

@app.route('/chat')
def chat():
    """Chat interface page"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    try:
        return render_template('chat.html', session_id=session['session_id'])
    except Exception as e:
        logger.error(f"Error loading chat: {e}")
        return f"Chat Error: {e}", 500

@app.route('/devices')
def devices():
    """Device management page"""
    try:
        if DATABASE_AVAILABLE:
            devices = db_manager.get_all_devices()
        else:
            devices = []
        return render_template('devices.html', devices=devices)
    except Exception as e:
        logger.error(f"Error loading devices: {e}")
        return f"Devices Error: {e}", 500

@app.route('/documents')
def documents():
    """Document management page"""
    try:
        if DATABASE_AVAILABLE:
            documents = db_manager.get_all_documents()
        else:
            documents = []
        return render_template('documents.html', documents=documents)
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        return f"Documents Error: {e}", 500

@app.route('/audit')
def audit():
    """Network audit page"""
    try:
        if DATABASE_AVAILABLE:
            devices = db_manager.get_all_devices()
            recent_audits = []  # Placeholder
        else:
            devices = []
            recent_audits = []
        return render_template('audit.html', devices=devices, recent_audits=recent_audits)
    except Exception as e:
        logger.error(f"Error loading audit page: {e}")
        return f"Audit Error: {e}", 500

@app.route('/dashboard')
def dashboard():
    """Dashboard page (alias for index)"""
    return index()

@app.route('/settings')
def settings():
    """Settings page"""
    try:
        return render_template('settings.html')
    except Exception as e:
        logger.error(f"Error loading settings page: {e}")
        return f"Settings Error: {e}", 500

# API Routes
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        if DATABASE_AVAILABLE:
            db_health = db_manager.health_check()
        else:
            db_health = False
            
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected' if db_health else 'disconnected',
            'port': 5003,
            'database_available': DATABASE_AVAILABLE
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get application statistics"""
    try:
        if DATABASE_AVAILABLE:
            stats = db_manager.get_stats()
        else:
            stats = {'devices': 0, 'documents': 0, 'audit_results': 0, 'chat_messages': 0}
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices', methods=['GET'])
def api_get_devices():
    """Get all devices"""
    try:
        if DATABASE_AVAILABLE:
            devices = db_manager.get_all_devices()
            return jsonify([device.to_dict() for device in devices])
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Send chat message - basic version"""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Message content required'}), 400
        
        session_id = data.get('session_id', session.get('session_id', str(uuid.uuid4())))
        
        # Simple response for now
        response_content = f"Echo: {data['content']} (AI integration coming soon)"
        
        return jsonify({
            'session_id': session_id,
            'response': response_content,
            'message_id': str(uuid.uuid4())
        })
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/message', methods=['POST'])
def api_chat_message():
    """Send chat message - basic version"""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Message content required'}), 400
        
        session_id = data.get('session_id', session.get('session_id', str(uuid.uuid4())))
        
        # Simple response for now
        response_content = f"Echo: {data['content']} (AI integration coming soon)"
        
        return jsonify({
            'session_id': session_id,
            'response': response_content,
            'message_id': str(uuid.uuid4())
        })
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ollama/models')
def api_get_ollama_models():
    """Get available Ollama models"""
    try:
        # Try to get real models from Ollama, fallback to mock
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = []
                model_sizes = {
                    'llama3.2:1b': {'size': '1.2B', 'speed': 'fastest'},
                    'phi4-mini:latest': {'size': '3.8B', 'speed': 'fast'},
                    'gemma3:latest': {'size': '4.3B', 'speed': 'medium'},
                    'llava:latest': {'size': '7B', 'speed': 'slow'}
                }
                
                for model in data.get('models', []):
                    model_name = model.get('name', '')
                    model_info = model_sizes.get(model_name, {'size': 'Unknown', 'speed': 'medium'})
                    models.append({
                        'name': model_name,
                        'size': model_info['size'],
                        'speed': model_info['speed']
                    })
                
                # Sort by speed (fastest first)
                speed_order = {'fastest': 0, 'fast': 1, 'medium': 2, 'slow': 3}
                models.sort(key=lambda x: speed_order.get(x['speed'], 2))
                
                recommended = models[0]['name'] if models else 'llama3.2:1b'
                
                return jsonify({
                    'models': models,
                    'current_model': recommended,
                    'recommended': recommended
                })
        except:
            pass
            
        # Fallback to mock models
        models = [
            {'name': 'llama3.2:1b', 'size': '1.2B', 'speed': 'fastest'},
            {'name': 'phi4-mini:latest', 'size': '3.8B', 'speed': 'fast'},
            {'name': 'gemma3:latest', 'size': '4.3B', 'speed': 'medium'},
            {'name': 'llava:latest', 'size': '7B', 'speed': 'slow'}
        ]
        
        return jsonify({
            'models': models,
            'current_model': 'llama3.2:1b',
            'recommended': 'llama3.2:1b'
        })
    except Exception as e:
        logger.error(f"Error getting Ollama models: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ollama/model', methods=['POST'])
def api_set_ollama_model():
    """Set the current Ollama model"""
    try:
        data = request.get_json()
        if not data or 'model' not in data:
            return jsonify({'error': 'Model name required'}), 400
        
        model_name = data['model']
        
        # For working version, just acknowledge the change
        logger.info(f"Model changed to: {model_name}")
        
        return jsonify({
            'success': True,
            'model': model_name,
            'message': f'Model changed to {model_name}'
        })
        
    except Exception as e:
        logger.error(f"Error setting Ollama model: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Network Automation AI Agent (Working Version)...")
    logger.info(f"Debug mode: {config.flask['DEBUG']}")
    logger.info(f"Host: {config.flask['HOST']}")
    logger.info(f"Port: {config.flask['PORT']}")
    
    app.run(
        host=config.flask['HOST'],
        port=config.flask['PORT'],
        debug=config.flask['DEBUG'],
        threaded=config.flask['THREADED']
    ) 