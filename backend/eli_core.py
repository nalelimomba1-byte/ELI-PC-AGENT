"""
ELI Core - Main orchestrator for the AI assistant
Coordinates all subsystems and manages the event loop
"""

import json
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional
from queue import Queue

from backend.voice.voice_engine import VoiceEngine
from backend.ai.nlp_processor import NLPProcessor
from backend.command_executor import CommandExecutor
from backend.web_automation import WebAutomation
from backend.screen_analyzer import ScreenAnalyzer
from backend.organization.task_manager import TaskManager
from backend.organization.scheduler import Scheduler
from backend.organization.note_system import NoteSystem

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EliCore:
    """Main ELI AI Assistant Core"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """Initialize ELI with configuration"""
        self.config = self._load_config(config_path)
        self.running = False
        self.command_queue = Queue()
        self.ui_callbacks = []
        self.status_callbacks = []
        
        # Initialize subsystems
        logger.info("Initializing ELI subsystems...")
        self.voice_engine = VoiceEngine(self.config['voice'], self.config['speech_recognition'])
        self.nlp_processor = NLPProcessor(self.config['ai'])
        self.command_executor = CommandExecutor(self.config['automation'])
        self.web_automation = WebAutomation()
        self.screen_analyzer = ScreenAnalyzer(self.config['ai'])
        self.task_manager = TaskManager()
        self.scheduler = Scheduler()
        self.note_system = NoteSystem()
        
        logger.info("ELI initialized successfully")
    
    def register_ui_callback(self, callback):
        """Register callback for UI updates (chat)"""
        self.ui_callbacks.append(callback)
        
    def register_status_callback(self, callback):
        """Register callback for status updates"""
        self.status_callbacks.append(callback)
        
    def _notify_ui(self, sender: str, message: str):
        """Send message to all registered UI callbacks"""
        for cb in self.ui_callbacks:
            try:
                cb(sender, message)
            except Exception as e:
                logger.error(f"UI Callback error: {e}")

    def _update_status(self, status: str, color: str = "gray"):
        """Send status update"""
        for cb in self.status_callbacks:
            try:
                cb(status, color)
            except Exception as e:
                logger.error(f"Status Callback error: {e}")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    def start(self):
        """Start ELI assistant"""
        logger.info("Starting ELI...")
        self.running = True
        
        # Start voice engine in separate thread
        voice_thread = threading.Thread(target=self._voice_loop, daemon=True)
        voice_thread.start()
        
        # Start scheduler
        scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        scheduler_thread.start()
        
        # Main command processing loop
        self._main_loop()
    
    def stop(self):
        """Stop ELI assistant"""
        logger.info("Stopping ELI...")
        self.running = False
        self.voice_engine.stop()
    
    def _voice_loop(self):
        """Voice recognition loop - runs in separate thread"""
        logger.info("Voice recognition active.")
        time.sleep(0.5) # Reduced startup wait
        # Queue welcome message instead of speaking directly
        self.command_queue.put({
            'type': 'feedback',
            'text': "Anny is ready"
        })
        
        while self.running:
            try:
                # Always listen for command (No wake word)
                command_text = self.voice_engine.listen()
                
                if command_text:
                    logger.info(f"Received command: {command_text}")
                    self._notify_ui("User", command_text)
                    self._update_status("Processing...", "yellow")
                    
                    # Check for STOP command
                    if "please and thank you" in command_text.lower():
                        self.command_queue.put({
                            'type': 'feedback',
                            'text': "Stopping. Goodbye!"
                        })
                        self.stop()
                        # Allow main loop to process shutdown before exit
                        time.sleep(2)
                        import os
                        os._exit(0) # Force exit
                        
                    self.command_queue.put({
                        'type': 'voice',
                        'text': command_text,
                        'timestamp': time.time()
                    })
                else:
                    # No speech detected, just loop fast
                    time.sleep(0.01) # Faster loop
                
            except Exception as e:
                logger.error(f"Error in voice loop: {e}")
                time.sleep(0.1)
    
    def _scheduler_loop(self):
        """Scheduler loop - runs in separate thread"""
        while self.running:
            try:
                # Check for scheduled tasks
                pending_tasks = self.scheduler.get_pending_tasks()
                
                for task in pending_tasks:
                    logger.info(f"Executing scheduled task: {task['name']}")
                    # Queue reminder speech
                    self.command_queue.put({
                        'type': 'feedback',
                        'text': f"Reminder: {task['name']}"
                    })
                    self.command_queue.put({
                        'type': 'scheduled',
                        'task': task,
                        'timestamp': time.time()
                    })
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(10)
    
    def _main_loop(self):
        """Main command processing loop"""
        logger.info("ELI is ready!")
        # Speak directly here is OK as it's main thread, but for consistency:
        # Speak directly here is OK as it's main thread, but for consistency:
        self.voice_engine.speak("ELI online and ready to assist")
        self._notify_ui("System", "ELI online and ready to assist")
        self._update_status("Listening", "green")
        
        while self.running:
            try:
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    
                    # Handle direct feedback (TTS)
                    if command.get('type') == 'feedback':
                        self.voice_engine.speak(command.get('text'))
                    else:
                        self._process_command(command)
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
    
    def _process_command(self, command: Dict[str, Any]):
        """Process a command from the queue"""
        try:
            command_text = command.get('text', '')
            
            # Parse intent using NLP
            intent = self.nlp_processor.parse_intent(command_text)
            logger.info(f"Parsed intent: {intent}")
            
            # Route to appropriate handler
            result = self._route_command(intent)
            
            # Provide feedback
            if result['success']:
                response = result.get('message', 'Done')
                logger.info(f"Command executed successfully: {response}")
                self._notify_ui("System", response)
                self.voice_engine.speak(response)
                self._update_status("Listening", "green")
            else:
                error_msg = result.get('error', 'Something went wrong')
                logger.error(f"Command failed: {error_msg}")
                self._notify_ui("System", f"Error: {error_msg}")
                self.voice_engine.speak(f"Sorry, {error_msg}")
                self._update_status("Error", "red")
                
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self.voice_engine.speak("I encountered an error processing that command")
    
    def _route_command(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Route command to appropriate subsystem"""
        action = intent.get('action', '')
        entities = intent.get('entities', {})
        
        try:
            # System commands (Extended)
            if action in ['open_app', 'close_app', 'system_command', 
                         'lock_pc', 'sleep_pc', 'empty_bin', 'check_battery', 
                         'set_brightness', 'volume_control', 'media_control']:
                return self.command_executor.execute(intent)
            
            # Web automation
            elif action in ['open_website', 'search_web', 'download']:
                return self.web_automation.execute(intent)
            
            elif action == 'play_media_online':
                return self.web_automation.play_media(entities.get('content'), entities.get('platform'))
            
            # Screen analysis
            elif action in ['take_screenshot', 'analyze_screen']:
                return self.screen_analyzer.execute(intent)
            
            # Task management
            elif action in ['create_task', 'list_tasks', 'complete_task']:
                return self.task_manager.execute(intent)
            
            # Scheduling
            elif action in ['schedule_event', 'set_reminder']:
                return self.scheduler.execute(intent)
            
            # Notes
            elif action in ['create_note', 'search_notes']:
                return self.note_system.execute(intent)
            
            # General query - use AI
            elif action == 'query':
                response = self.nlp_processor.generate_response(intent)
                return {'success': True, 'message': response}
            
            else:
                # Fallback: If action is unknown (e.g., 'greeting', 'compliment'), send to LLM as query
                logger.info(f"Unknown action '{action}', falling back to LLM query")
                
                # Construct a query from the raw text
                intent['action'] = 'query'
                intent['entities']['query'] = intent.get('raw_text', '')
                
                response = self.nlp_processor.generate_response(intent)
                return {'success': True, 'message': response}
                
        except Exception as e:
            logger.error(f"Error routing command: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_text_command(self, text: str) -> Dict[str, Any]:
        """Process a text command (for UI/API interface)"""
        self.command_queue.put({
            'type': 'text',
            'text': text,
            'timestamp': time.time()
        })
        return {'status': 'queued'}


if __name__ == "__main__":
    # Create and start ELI
    eli = EliCore()
    
    try:
        eli.start()
    except KeyboardInterrupt:
        eli.stop()
        logger.info("ELI shutdown complete")
