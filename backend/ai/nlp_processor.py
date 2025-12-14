"""
NLP Processor - Natural language understanding and intent classification
"""

import logging
import re
from typing import Dict, Any, List, Optional
import json
from backend.ai.llm_integration import LLMIntegration

logger = logging.getLogger(__name__)


from backend.ai.anny_brain import AnnyBrain

class NLPProcessor:
    """Natural Language Processor using Custom ANNY Brain"""
    
    def __init__(self, ai_config: dict):
        """Initialize NLP processor"""
        self.config = ai_config
        self.brain = AnnyBrain()
        
        # Try loading custom brain
        if self.brain.load_brain():
            logger.info("✅ Custom ANNY Brain loaded successfully")
        else:
            logger.warning("⚠️ Could not load ANNY Brain. Using fallback patterns.")
            # Trigger background training if needed
            # self.brain.train() 

        # Initialize Fallback LLM (if configured)
        self.llm = LLMIntegration(ai_config)
        
        # Intent patterns (rule-based for common commands) - Kept for fallback
        self.intent_patterns = self._load_intent_patterns()
        
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent recognition patterns"""
        return {
            # Application control
            'open_app': [
                r'open\s+(\w+)',
                r'launch\s+(\w+)',
                r'start\s+(\w+)',
                r'run\s+(\w+)'
            ],
            'close_app': [
                r'close\s+(\w+)',
                r'quit\s+(\w+)',
                r'exit\s+(\w+)',
                r'stop\s+(\w+)'
            ],
            
            # Web browsing
            'open_website': [
                r'open\s+(https?://\S+)',
                r'go\s+to\s+(\S+\.\S+)',
                r'browse\s+(\S+)',
                r'visit\s+(\S+)'
            ],
            'search_web': [
                r'search\s+(?:for\s+)?(.+)',
                r'google\s+(.+)',
                r'look\s+up\s+(.+)',
                r'find\s+(.+)'
            ],
            
            # File operations
            'create_file': [
                r'create\s+(?:a\s+)?file\s+(?:named\s+)?(.+)',
                r'make\s+(?:a\s+)?file\s+(.+)',
                r'new\s+file\s+(.+)'
            ],
            'create_folder': [
                r'create\s+(?:a\s+)?folder\s+(?:named\s+)?(.+)',
                r'make\s+(?:a\s+)?(?:directory|folder)\s+(.+)',
                r'new\s+folder\s+(.+)'
            ],
            'delete_file': [
                r'delete\s+(?:the\s+)?file\s+(.+)',
                r'remove\s+(?:the\s+)?file\s+(.+)'
            ],
            
            # Task management
            'create_task': [
                r'create\s+(?:a\s+)?task\s+(.+)',
                r'add\s+(?:a\s+)?task\s+(.+)',
                r'new\s+task\s+(.+)',
                r'remind\s+me\s+to\s+(.+)'
            ],
            'list_tasks': [
                r'(?:show|list|what\s+are)\s+(?:my\s+)?tasks',
                r'what\s+do\s+i\s+need\s+to\s+do',
                r'show\s+(?:my\s+)?to-?do'
            ],
            'complete_task': [
                r'complete\s+task\s+(.+)',
                r'mark\s+(.+)\s+as\s+done',
                r'finish\s+task\s+(.+)'
            ],
            
            # Scheduling
            'schedule_event': [
                r'schedule\s+(.+)',
                r'add\s+(?:to\s+)?(?:my\s+)?calendar\s+(.+)',
                r'create\s+(?:an\s+)?event\s+(.+)'
            ],
            'set_reminder': [
                r'remind\s+me\s+(?:to\s+)?(.+)',
                r'set\s+(?:a\s+)?reminder\s+(.+)'
            ],
            
            # Notes
            'create_note': [
                r'(?:take|create|make)\s+(?:a\s+)?note\s+(.+)',
                r'note\s+(?:that\s+)?(.+)',
                r'write\s+down\s+(.+)'
            ],
            'search_notes': [
                r'find\s+(?:my\s+)?notes?\s+(?:about\s+)?(.+)',
                r'search\s+notes?\s+(?:for\s+)?(.+)'
            ],
            
            # System commands
            'volume_control': [
                r'(?:set\s+)?volume\s+(?:to\s+)?(\d+)',
                r'(?:turn\s+)?volume\s+(up|down)',
                r'(mute|unmute)'
            ],
            'set_brightness': [
                r'(?:set\s+)?brightness\s+(?:to\s+)?(\d+)',
                r'(?:turn\s+)?brightness\s+(up|down)',
                r'dim\s+(?:the\s+)?screen'
            ],
            'lock_pc': [
                r'lock\s+(?:the\s+)?(pc|computer|screen|workstation)',
                r'secure\s+(?:the\s+)?(pc|computer)'
            ],
            'sleep_pc': [
                r'(?:put\s+)?(?:the\s+)?(pc|computer)\s+to\s+sleep',
                r'sleep\s+(?:the\s+)?(pc|computer)',
                r'hibernate\s+(?:the\s+)?(pc|computer)'
            ],
            'empty_bin': [
                r'empty\s+(?:the\s+)?(?:recycle\s+)?bin',
                r'empty\s+trash',
                r'clear\s+(?:recycle\s+)?bin'
            ],
            'check_battery': [
                r'(?:check\s+)?battery\s+(?:status|level|percentage)',
                r'how\s+is\s+(?:my\s+)?battery',
                r'how\s+much\s+battery\s+(?:do\s+i\s+have)?'
            ],
            'media_control': [
                r'(play|pause|stop|next|previous)',
                r'(play|pause)\s+music'
            ],
            
            # Screen commands
            'take_screenshot': [
                r'take\s+(?:a\s+)?screenshot',
                r'capture\s+(?:the\s+)?screen',
                r'snapshot'
            ],
            'analyze_screen': [
                r'(?:analyze|read|describe)\s+(?:the\s+)?screen',
                r'what\s+is\s+on\s+(?:my\s+)?screen',
                r'what\s+am\s+i\s+looking\s+at'
            ],
            
            # Smart Media
            'play_media_online': [
                r'play\s+(.+)\s+on\s+(youtube|spotify)',
                r'search\s+(?:for\s+)?(.+)\s+on\s+(youtube|spotify)'
            ],
            
            # Weather
            'weather': [
                r'weather\s+(?:in\s+)?(.+)',
                r'what\s+is\s+the\s+weather',
                r'is\s+it\s+raining'
            ],
            
            # Timer/Alarm
            'timer': [
                r'set\s+(?:a\s+)?timer\s+(?:for\s+)?(.+)',
                r'timer\s+for\s+(.+)'
            ],
            'alarm': [
                r'set\s+(?:an\s+)?alarm\s+(?:for\s+)?(.+)',
                r'wake\s+me\s+up\s+(?:at\s+)?(.+)'
            ],
            
            # File Management
            'file_move': [
                r'move\s+(.+)\s+to\s+(.+)',
                r'transfer\s+(.+)\s+to\s+(.+)'
            ],
            
            # Downloads
            'download': [
                r'download\s+(.+)',
                r'get\s+(.+)\s+from\s+(.+)'
            ],
            
            # General query (fallback)
            #'query': [
            #    r'what\s+is\s+(.+)',
            #    r'who\s+is\s+(.+)',
            #    r'how\s+(?:do\s+i\s+)?(.+)',
            #    r'tell\s+me\s+about\s+(.+)'
            #]
            # Rely on Step 3 Fallback instead of regex for queries to allow brain to work
        }
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parse user input and extract intent and entities
        
        Args:
            text: User input text
            
        Returns:
            Dictionary with action, entities, and confidence
        """
        text = text.lower().strip()
        
        # 1. Try pattern matching first (High Confidence)
        for action, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities = self._extract_entities(action, match, text)
                    
                    intent = {
                        'action': action,
                        'entities': entities,
                        'confidence': 1.0, # Exact match
                        'raw_text': text
                    }
                    
                    logger.info(f"Matched intent (Regex): {action}")
                    return intent
        
        # 2. Try ANNY Brain (Neural Network) (Medium-High Confidence)
        if self.brain.is_trained:
            tag, confidence = self.brain.predict(text)
            logger.info(f"Brain Prediction: {tag} ({confidence:.2f})")
            
            if confidence > 0.7:  # Confidence threshold
                # Extract entities based on predicted tag (heuristic extraction since NN only gives tag)
                # We reuse _extract_entities but pass a dummy match or use text analysis
                entities = self._extract_entities_from_text(tag, text)
                
                # Normalize tags if necessary (map complex_media -> volume_control/media_control if needed)
                # For now, we assume tags match actions or are mapped later.
                
                # Map 'complex_media' to 'volume_control' or others based on keywords as fallback logic
                if tag == 'complex_media':
                    if 'volume' in text or 'turn it' in text or 'louder' in text or 'quieter' in text:
                        tag = 'volume_control'
                        # Attempt to extract volume entities manually since regex failed
                        if 'up' in text or 'louder' in text: entities['action'] = 'up'
                        elif 'down' in text or 'quieter' in text: entities['action'] = 'down'
                
                intent = {
                    'action': tag,
                    'entities': entities,
                    'confidence': float(confidence),
                    'raw_text': text
                }
                return intent

        # 3. Fallback: General Query (Low Confidence)
        logger.info("No specific intent matched, treating as general query")
        return {
            'action': 'query',
            'entities': {'query': text},
            'confidence': 0.5,
            'raw_text': text
        }
    
    def _extract_entities(self, action: str, match: re.Match, text: str) -> Dict[str, Any]:
        """Extract entities based on action type"""
        entities = {}
        
        if action in ['open_app', 'close_app']:
            entities['app_name'] = match.group(1)
        
        elif action == 'open_website':
            url = match.group(1)
            if not url.startswith('http'):
                url = 'https://' + url
            entities['url'] = url
        
        elif action == 'search_web':
            entities['query'] = match.group(1)
        
        elif action in ['create_file', 'create_folder', 'delete_file']:
            entities['name'] = match.group(1)
        
        elif action in ['create_task', 'complete_task']:
            entities['task_name'] = match.group(1)
            # Extract time/date if present
            entities['due_date'] = self._extract_datetime(text)
        
        elif action == 'schedule_event':
            entities['event_name'] = match.group(1)
            entities['datetime'] = self._extract_datetime(text)
        
        elif action == 'set_reminder':
            entities['reminder_text'] = match.group(1)
            entities['datetime'] = self._extract_datetime(text)
        
        elif action in ['create_note', 'search_notes']:
            entities['content'] = match.group(1)
        
        elif action == 'volume_control':
            if match.group(1) in ['mute', 'unmute']:
                entities['action'] = match.group(1)
            elif match.group(1).isdigit():
                entities['level'] = int(match.group(1))
            else:
                entities['action'] = match.group(1)
                
        elif action == 'set_brightness':
            text_lower = text.lower()
            if 'dim' in text_lower:
                entities['level'] = 30  # Dim to 30%
            elif match.group(1) and match.group(1).isdigit():
                entities['level'] = int(match.group(1))
            else:
                entities['action'] = match.group(1)
        
        elif action == 'sleep_pc':
            if 'hibernate' in text.lower():
                entities['mode'] = 'hibernate'
            else:
                entities['mode'] = 'suspend'
                
        elif action == 'analyze_screen':
            # Use whole text as query if it's a question, or standard prompt
            entities['query'] = text
        
        elif action == 'play_media_online':
            entities['content'] = match.group(1)
            entities['platform'] = match.group(2)
        
        elif action == 'media_control':
            entities['action'] = match.group(1)
        
        elif action == 'download':
            entities['url'] = match.group(1)
        
        elif action == 'query':
            entities['query'] = match.group(1) if match.groups() else text
            
        elif action == 'timer' or action == 'alarm':
            entities['datetime'] = self._extract_datetime(text)
            
        elif action == 'weather':
            entities['location'] = match.group(1).strip()
            
        elif action == 'file_move':
             entities['source'] = match.group(1).strip()
             entities['destination'] = match.group(2).strip()
             
        elif action == 'timer' or action == 'alarm':
             entities['datetime'] = match.group(1).strip()
        
        return entities
    
    def _extract_entities_from_text(self, action: str, text: str) -> Dict[str, Any]:
        """
        Extract entities when proper regex match isn't available (Brain path)
        """
        entities = {}
        
        if action == 'timer' or action == 'alarm':
             entities['datetime'] = self._extract_datetime(text)
             # Extract explicit time if not caught by datetime
             import re
             minutes = re.search(r'(\d+)\s*min', text)
             if minutes:
                 entities['duration'] = int(minutes.group(1))
                 
        elif action == 'weather':
            # Extract location "in [Location]"
            import re
            loc = re.search(r'in\s+([a-zA-Z\s]+)', text)
            if loc:
                entities['location'] = loc.group(1).strip()
                
        elif action == 'file_move':
            # Try to infer source/dest
            import re
            # "Move X to Y"
            move_match = re.search(r'move\s+(.+)\s+to\s+(.+)', text)
            if move_match:
                entities['source'] = move_match.group(1).strip()
                entities['destination'] = move_match.group(2).strip()
        
        elif action == 'volume_control':
             if 'up' in text or 'louder' in text: entities['action'] = 'up'
             elif 'down' in text or 'quieter' in text: entities['action'] = 'down'
             elif 'mute' in text: entities['action'] = 'mute'
             
        # Add original query as fallback
        entities['query'] = text
        return entities
    
    def _extract_datetime(self, text: str) -> Optional[str]:
        """Extract datetime information from text"""
        # Simple datetime extraction (can be enhanced with dateparser library)
        datetime_patterns = [
            r'(?:at\s+)?(\d{1,2}:\d{2}(?:\s*[ap]m)?)',
            r'(?:on\s+)?(\w+day)',
            r'(?:in\s+)?(\d+)\s+(minute|hour|day)s?',
            r'(tomorrow|today|tonight)',
        ]
        
        for pattern in datetime_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def generate_response(self, intent: Dict[str, Any]) -> str:
        """
        Generate natural language response using AI
        """
        query = intent.get('entities', {}).get('query', '')
        
        # Use LLM to generate response
        try:
            # Check if it's a simple query or needs context
            response = self.llm.generate_response(query)
            
            # Record in context
            self.add_to_context(query, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return f"I understand you're asking about: {query}, but I'm having trouble connecting to my AI brain right now."
    
    def add_to_context(self, text: str, response: str):
        """Add interaction to context history"""
        self.context_history.append({
            'user': text,
            'assistant': response
        })
        
        # Keep only recent context
        if len(self.context_history) > self.max_context:
            self.context_history.pop(0)


if __name__ == "__main__":
    # Test NLP processor
    logging.basicConfig(level=logging.INFO)
    
    processor = NLPProcessor({'context_window': 10})
    
    test_commands = [
        "open chrome",
        "search for python tutorials",
        "create a task to buy groceries tomorrow",
        "remind me to call mom at 5pm",
        "what is the weather like",
        "volume up",
        "play music"
    ]
    
    for cmd in test_commands:
        print(f"\nCommand: {cmd}")
        intent = processor.parse_intent(cmd)
        print(f"Intent: {json.dumps(intent, indent=2)}")
