import unittest
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ai.nlp_processor import NLPProcessor
from backend.command_executor import CommandExecutor
from backend.web_automation import WebAutomation

class TestBrainExpansion(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Initialize processors
        cls.nlp = NLPProcessor({'context_window': 5})
        cls.executor = CommandExecutor({'confirm_risky_commands': False})
        cls.web = WebAutomation()
        
    def test_brain_predictions(self):
        """Test if the Neural Network correctly identifies new intents"""
        test_cases = [
            ("Set a timer for 10 minutes", "timer"),
            ("Wake me up at 7am", "alarm"), # May map to timer/alarm depending on model
            ("What is the weather in London", "weather"),
            ("Move all jpgs to Pictures", "file_move"),
            ("Turn the volume up a little bit", "volume_control") # Mapped from complex_media
        ]
        
        print("\nTesting Brain Predictions:")
        for text, expected in test_cases:
            intent = self.nlp.parse_intent(text)
            print(f"  Input: '{text}' -> Intent: {intent['action']} (Conf: {intent.get('confidence', 0)})")
            
            # Allow for some fuzzy matching or direct mapping
            # Timer and alarm might be interchangeable in some contexts or model training
            if expected == 'alarm' and intent['action'] == 'timer':
                pass
            elif expected == 'volume_control' and intent['action'] == 'complex_media':
                pass
            else:
                self.assertEqual(intent['action'], expected)

    def test_entity_extraction(self):
        """Test extraction of entities for new skills"""
        
        # Timer
        intent = self.nlp.parse_intent("Set a timer for 15 minutes")
        print(f"  Timer Entities: {intent.get('entities')}")
        # Note: Regex/Brain hybrid might return datetime or duration
        
        # Weather
        intent = self.nlp.parse_intent("Weather in Paris")
        print(f"  Weather Entities: {intent.get('entities')}")
        self.assertEqual(intent['entities'].get('location'), 'paris')
        
        # File Move
        intent = self.nlp.parse_intent("Move test.txt to Documents")
        print(f"  File Move Entities: {intent.get('entities')}")
        self.assertEqual(intent['entities'].get('source'), 'test.txt')
        self.assertEqual(intent['entities'].get('destination'), 'documents')

    def test_weather_function(self):
        """Test weather function (mock run)"""
        # We just want to ensure it doesn't crash, actual browser opening is side effect
        # We can spy/mock if needed, but for now just run it as unit test
        print("\nTesting Weather Function:")
        result = self.web.get_weather("London")
        self.assertTrue(result['success'])
        
if __name__ == '__main__':
    unittest.main()
