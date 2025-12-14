"""
LLM Integration - Integration with AI models for complex queries
"""

import logging
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class LLMIntegration:
    """Integrates with LLM APIs for advanced natural language processing"""
    
    def __init__(self, ai_config: dict):
        """Initialize LLM integration"""
        self.config = ai_config
        self.provider = ai_config.get('provider', 'openai')
        self.model = ai_config.get('model', 'gpt-4')
        self.conversation_history = []
        
        # Initialize API client
        self.client = None
        self._initialize_client()
        
        logger.info(f"LLM integration initialized with {self.provider}")
    
    def _initialize_client(self):
        """Initialize the appropriate API client"""
        try:
            if self.provider == 'openai':
                import openai
                api_key = os.getenv('OPENAI_API_KEY') or self.config.get('api_key')
                if api_key:
                    openai.api_key = api_key
                    self.client = openai
                    logger.info("OpenAI client initialized")
                else:
                    logger.warning("No OpenAI API key found")
            
            elif self.provider == 'anthropic':
                from anthropic import Anthropic
                api_key = os.getenv('ANTHROPIC_API_KEY') or self.config.get('api_key')
                if api_key:
                    self.client = Anthropic(api_key=api_key)
                    logger.info("Anthropic client initialized")
                else:
                    logger.warning("No Anthropic API key found")
                    
            elif self.provider == 'google':
                import google.generativeai as genai
                api_key = os.getenv('GOOGLE_API_KEY') or self.config.get('api_key')
                if api_key:
                    genai.configure(api_key=api_key)
                    self.client = genai
                    logger.info("Google Gemini client initialized")
                else:
                    logger.warning("No Google API key found")

            elif self.provider == 'offline':
                logger.info("ELI starting in OFFLINE mode. No API key required.")
                self.client = "offline_dummy"
            
        except ImportError as e:
            logger.error(f"Failed to import {self.provider} library: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
    
    def generate_response(self, query: str, context: Optional[List[Dict]] = None) -> str:
        """Generate response using LLM"""
        if not self.client:
            return "I don't have access to advanced AI capabilities right now. Please configure an API key."
        
        try:
            # Build messages
            messages = self._build_messages(query, context)
            
            # Generate response based on provider
            if self.provider == 'openai':
                response = self._generate_openai(messages)
            elif self.provider == 'anthropic':
                response = self._generate_anthropic(messages)
            elif self.provider == 'google':
                response = self._generate_google(messages)
            elif self.provider == 'offline':
                response = "I am in Offline Mode. I can control your PC (Apps, Volume, Brightness, Lock, Sleep) but I cannot answer general questions."
            else:
                response = "Unsupported AI provider"
            
            # Add to conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': query
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': response
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return "I encountered an error processing your request."

    def _generate_google(self, messages: List[Dict]) -> str:
        """Generate response using Google Gemini"""
        try:
            # Gemini uses a different message format
            # We'll use the latest user message + system context
            model = self.client.GenerativeModel(self.model)
            
            # Construct prompt from messages
            prompt = ""
            for msg in messages:
                role = msg['role']
                content = msg['content']
                if role == 'system':
                    prompt += f"System: {content}\n"
                elif role == 'user':
                    prompt += f"User: {content}\n"
                elif role == 'assistant':
                    prompt += f"Model: {content}\n"
            
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Google API error: {e}")
            raise

    def _build_messages(self, query: str, context: Optional[List[Dict]] = None) -> List[Dict]:
        """Build message list for API call"""
        messages = [
            {
                'role': 'system',
                'content': '''You are ELI, an advanced AI assistant. 
                You are helpful, efficient, and professional. You can help with:
                - Answering questions and providing information
                - Managing tasks and schedules
                - Controlling system operations
                - Web browsing and research
                - File and folder management
                
                Keep responses concise and actionable. When you don't know something, admit it.
                Always be respectful and maintain a professional yet friendly tone.'''
            }
        ]
        
        # Add context if provided
        if context:
            messages.extend(context)
        
        # Add recent conversation history
        messages.extend(self.conversation_history[-6:])  # Last 3 exchanges
        
        # Add current query
        messages.append({
            'role': 'user',
            'content': query
        })
        
        return messages
    
    def _generate_openai(self, messages: List[Dict]) -> str:
        """Generate response using OpenAI"""
        try:
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=self.config.get('max_tokens', 500),
                temperature=self.config.get('temperature', 0.7)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _generate_anthropic(self, messages: List[Dict]) -> str:
        """Generate response using Anthropic"""
        try:
            # Convert messages format for Anthropic
            system_message = next((m['content'] for m in messages if m['role'] == 'system'), '')
            user_messages = [m for m in messages if m['role'] != 'system']
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.config.get('max_tokens', 500),
                system=system_message,
                messages=user_messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def generate_vision_response(self, query: str, image_path: str) -> str:
        """Generate response based on image and text query (Vision)"""
        if not self.client:
            return "I don't have access to AI vision capabilities right now."
            
        try:
            if self.provider == 'google':
                import PIL.Image
                # Use the configured model, as modern Gemini models are multimodal
                model = self.client.GenerativeModel(self.model)
                img = PIL.Image.open(image_path)
                
                response = model.generate_content([query, img])
                return response.text
                
            import base64
            
            # Encode image
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            if self.provider == 'openai':
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": query},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_image}"
                                }
                            }
                        ]
                    }
                ]
                # Use GPT-4o or Vision model if not specified
                model = self.model if 'vision' in self.model or 'gpt-4o' in self.model else 'gpt-4o'
                
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=500
                )
                return response.choices[0].message.content
                
            elif self.provider == 'anthropic':
                # Determine media type based on extension
                import mimetypes
                media_type, _ = mimetypes.guess_type(image_path)
                if not media_type:
                    media_type = "image/jpeg"
                
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20240620", # Use capable vision model
                    max_tokens=500,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": encoded_image
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": query
                                }
                            ]
                        }
                    ]
                )
                return message.content[0].text
                
        except Exception as e:
            logger.error(f"Vision API error: {e}")
            return f"I couldn't analyze the screen: {str(e)}"

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")


if __name__ == "__main__":
    # Test LLM integration
    logging.basicConfig(level=logging.INFO)
    
    config = {
        'provider': 'openai',
        'model': 'gpt-4',
        'max_tokens': 500,
        'temperature': 0.7
    }
    
    llm = LLMIntegration(config)
    
    # Test query
    response = llm.generate_response("What can you help me with?")
    print(f"Response: {response}")
