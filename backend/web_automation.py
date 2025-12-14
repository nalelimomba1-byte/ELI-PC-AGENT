"""
Web Automation - Browser automation and web interactions
"""

import logging
import webbrowser
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class WebAutomation:
    """Handles web browsing and automation tasks"""
    
    def __init__(self):
        """Initialize web automation"""
        self.download_path = Path.home() / 'Downloads'
        logger.info("Web automation initialized")
    
    def execute(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute web automation command
        
        Args:
            intent: Parsed intent from NLP processor
            
        Returns:
            Result dictionary
        """
        action = intent.get('action')
        entities = intent.get('entities', {})
        
        try:
            if action == 'open_website':
                return self._open_website(entities.get('url'))
            
            elif action == 'search_web':
                return self._search_web(entities.get('query'))
            
            elif action == 'download':
                return self._download_file(entities.get('url'))
                
            elif action == 'weather':
                return self.get_weather(entities.get('location', ''))
            
            else:
                return {'success': False, 'error': f'Unknown web action: {action}'}
                
        except Exception as e:
            logger.error(f"Web automation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _open_website(self, url: str) -> Dict[str, Any]:
        """Open a website in default browser"""
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            logger.info(f"Opened website: {url}")
            
            return {'success': True, 'message': f'Opening {url}'}
            
        except Exception as e:
            logger.error(f"Failed to open website: {e}")
            return {'success': False, 'error': str(e)}
    
    def _search_web(self, query: str) -> Dict[str, Any]:
        """Search the web using default search engine"""
        try:
            # Use Google search
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            webbrowser.open(search_url)
            
            logger.info(f"Searching for: {query}")
            return {'success': True, 'message': f'Searching for {query}'}
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _download_file(self, url: str) -> Dict[str, Any]:
        """Download a file from URL"""
        try:
            # Get filename from URL
            filename = url.split('/')[-1] or 'download'
            filepath = self.download_path / filename
            
            logger.info(f"Downloading {url} to {filepath}")
            
            # Download file
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Download complete: {filepath}")
            return {'success': True, 'message': f'Downloaded {filename}'}
            
        except requests.RequestException as e:
            logger.error(f"Download failed: {e}")
            return {'success': False, 'error': f'Download failed: {str(e)}'}
        except Exception as e:
            logger.error(f"Download error: {e}")
            return {'success': False, 'error': str(e)}
    
    def search_and_extract(self, query: str) -> Dict[str, Any]:
        """
        Search web and extract information (No-AI implementation)
        """
        # Try Wikipedia for informational queries
        try:
            import wikipedia
            # Simple heuristic: if query is short or looks like a topic
            summary = wikipedia.summary(query, sentences=2)
            return {'success': True, 'message': summary, 'source': 'Wikipedia'}
        except Exception as e:
            logger.info(f"Wikipedia lookup failed: {e}")
            
        # Fallback to opening search
        return self._search_web(query)

    def play_media(self, content: str, platform: str = 'youtube') -> Dict[str, Any]:
        """Play media on specific platform"""
        try:
            platform = platform.lower()
            
            if 'youtube' in platform:
                # Open specific YouTube search/video
                url = f"https://www.youtube.com/results?search_query={quote_plus(content)}"
                self._open_website(url)
                # Note: To auto-play first video requires selenium, this opens search results
                return {'success': True, 'message': f'Searching for {content} on YouTube'}
                
            elif 'spotify' in platform:
                # Open Spotify Web Player search
                url = f"https://open.spotify.com/search/{quote_plus(content)}"
                self._open_website(url)
                return {'success': True, 'message': f'Searching for {content} on Spotify'}
            
            else:
                # Default to YouTube
                return self.play_media(content, 'youtube')
                
        except Exception as e:
            logger.error(f"Media play failed: {e}")
            return {'success': False, 'error': str(e)}

    def get_weather(self, location: str = "") -> Dict[str, Any]:
        """Get weather info (by opening weather site for now)"""
        try:
            if not location:
                location = "my location"
            
            # Open Google Weather
            self._search_web(f"weather in {location}")
            
            # Simple speech response for now (since we can't scrape easily without heavy tooling)
            return {'success': True, 'message': f'Showing weather for {location}'}
            
        except Exception as e:
            logger.error(f"Weather failed: {e}")
            return {'success': False, 'error': str(e)}


if __name__ == "__main__":
    # Test web automation
    logging.basicConfig(level=logging.INFO)
    
    web = WebAutomation()
    
    # Test search
    result = web.execute({
        'action': 'search_web',
        'entities': {'query': 'Python tutorials'}
    })
    print(result)
