"""
Screen Analyzer - Handles screen capture and vision capabilities
"""

import logging
import pyautogui
from pathlib import Path
import os
import time
from typing import Dict, Any, Optional

from backend.ai.llm_integration import LLMIntegration

logger = logging.getLogger(__name__)

class ScreenAnalyzer:
    """Handles screen operations and analysis"""
    
    def __init__(self, ai_config: dict = None):
        """Initialize screen analyzer"""
        self.screenshots_dir = Path.home() / 'Pictures' / 'ELI Screenshots'
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize LLM for vision
        self.llm = None
        if ai_config:
            self.llm = LLMIntegration(ai_config)
            
        logger.info("Screen analyzer initialized")
        
    def execute(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Execute screen-related commands"""
        action = intent.get('action')
        
        try:
            if action == 'take_screenshot':
                return self.take_screenshot()
            
            elif action == 'analyze_screen':
                query = intent.get('entities', {}).get('query', 'Describe what is on the screen')
                return self.analyze_screen(query)
                
            else:
                return {'success': False, 'error': f'Unknown screen action: {action}'}
        except Exception as e:
            logger.error(f"Screen operation failed: {e}")
            return {'success': False, 'error': str(e)}
            
    def take_screenshot(self) -> Dict[str, Any]:
        """Capture full screen screenshot"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            logger.info(f"Screenshot saved: {filepath}")
            
            # Only open folder if explicitly taking a screenshot, not for analysis
            # os.startfile(self.screenshots_dir) 
            
            return {
                'success': True, 
                'message': f'Screenshot saved to {filename}',
                'path': str(filepath)
            }
            
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return {'success': False, 'error': f'Failed to take screenshot: {e}'}

    def analyze_screen(self, query: str) -> Dict[str, Any]:
        """Take screenshot and analyze with Vision AI"""
        try:
            # 1. Take screenshot (but don't open folder)
            result = self.take_screenshot()
            if not result['success']:
                return result
                
            image_path = result['path']
            
            # 2. Send to Vision AI
            if self.llm:
                analysis = self.llm.generate_vision_response(query, image_path)
                return {
                    'success': True,
                    'message': analysis,
                    'image_path': image_path
                }
            else:
                return {
                    'success': False, 
                    'error': 'Vision AI not configured (missing AI config)'
                }
                
        except Exception as e:
            logger.error(f"Screen analysis failed: {e}")
            return {'success': False, 'error': str(e)}
