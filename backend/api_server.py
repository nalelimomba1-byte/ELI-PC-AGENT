"""
Flask API Server for ELI
Provides HTTP endpoints for frontend communication
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from backend.eli_core import EliCore
import pyttsx3
import threading

app = Flask(__name__)
CORS(app)

# Initialize ELI
eli = None

# Initialize TTS engine
tts_engine = None
tts_lock = threading.Lock()

def speak_text(text):
    """Speak text using pyttsx3"""
    global tts_engine
    try:
        with tts_lock:
            if tts_engine is None:
                tts_engine = pyttsx3.init()
                tts_engine.setProperty('rate', 150)
                tts_engine.setProperty('volume', 1.0)
            
            tts_engine.say(text)
            tts_engine.runAndWait()
    except Exception as e:
        logging.error(f"TTS error: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'ELI AI Assistant'
    })


@app.route('/command', methods=['POST'])
def process_command():
    """Process a text command"""
    try:
        data = request.json
        # Accept both 'command' and 'text' for compatibility
        command_text = data.get('command') or data.get('text', '')
        
        if not command_text:
            return jsonify({
                'success': False,
                'error': 'No command provided'
            }), 400
        
        logger.info(f"Processing command: {command_text}")
        
        # Process command through NLP
        intent_data = eli.nlp_processor.parse_intent(command_text)
        
        # Generate response based on intent
        action = intent_data.get('action')
        
        if action == 'open_app':
            result = eli.command_executor.execute(intent_data)
        elif action in ['create_task', 'list_tasks', 'complete_task']:
            result = eli.task_manager.execute(intent_data)
        else:
            # Use NLP to generate response for general queries
            response = eli.nlp_processor.generate_response(intent_data)
            result = {'success': True, 'response': response}
        
        # Speak the response
        if result.get('response'):
            threading.Thread(target=speak_text, args=(result['response'],), daemon=True).start()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Command processing error: {e}")
        import traceback
        traceback.print_exc()
        
        error_msg = f"Sorry, I encountered an error"
        
        # Speak error message
        threading.Thread(target=speak_text, args=(error_msg,), daemon=True).start()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'response': error_msg
        }), 500


@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    try:
        result = eli.task_manager.execute({
            'action': 'list_tasks',
            'entities': {}
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to get tasks: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.json
        
        result = eli.task_manager.execute({
            'action': 'create_task',
            'entities': data
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'online',
        'voice': True,
        'backend': True,
        'tasks': len(eli.task_manager.tasks),
        'notes': len(eli.note_system.notes)
    })


def run_server(eli_instance, host='127.0.0.1', port=5000):
    """Run Flask server"""
    global eli
    eli = eli_instance
    
    logger.info(f"Starting API server on {host}:{port}")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    # For testing
    from backend.eli_core import EliCore
    
    eli_core = EliCore()
    run_server(eli_core)
