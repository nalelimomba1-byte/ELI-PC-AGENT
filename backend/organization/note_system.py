"""
Note System - Quick note-taking and knowledge management
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Note:
    """Note data structure"""
    id: str
    title: str
    content: str
    created_at: str = ""
    updated_at: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        if self.tags is None:
            self.tags = []


class NoteSystem:
    """Manages notes and knowledge base"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize note system"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.notes_file = self.data_dir / "notes.json"
        self.notes: List[Note] = []
        
        self._load_notes()
        logger.info(f"Note system initialized with {len(self.notes)} notes")
    
    def _load_notes(self):
        """Load notes from file"""
        try:
            if self.notes_file.exists():
                with open(self.notes_file, 'r') as f:
                    data = json.load(f)
                    self.notes = [Note(**note) for note in data]
                logger.info(f"Loaded {len(self.notes)} notes")
        except Exception as e:
            logger.error(f"Failed to load notes: {e}")
            self.notes = []
    
    def _save_notes(self):
        """Save notes to file"""
        try:
            with open(self.notes_file, 'w') as f:
                json.dump([asdict(note) for note in self.notes], f, indent=2)
            logger.info("Notes saved")
        except Exception as e:
            logger.error(f"Failed to save notes: {e}")
    
    def execute(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Execute note operation"""
        action = intent.get('action')
        entities = intent.get('entities', {})
        
        try:
            if action == 'create_note':
                return self._create_note(entities)
            
            elif action == 'search_notes':
                return self._search_notes(entities)
            
            else:
                return {'success': False, 'error': f'Unknown note action: {action}'}
                
        except Exception as e:
            logger.error(f"Note operation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_note(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new note"""
        try:
            content = entities.get('content', '')
            
            # Extract title from first line or use first few words
            lines = content.split('\n')
            title = lines[0][:50] if lines else content[:50]
            
            note = Note(
                id=str(uuid.uuid4()),
                title=title,
                content=content
            )
            
            self.notes.append(note)
            self._save_notes()
            
            logger.info(f"Created note: {title}")
            return {'success': True, 'message': f'Note created: {title}'}
            
        except Exception as e:
            logger.error(f"Failed to create note: {e}")
            return {'success': False, 'error': str(e)}
    
    def _search_notes(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Search notes by content"""
        try:
            query = entities.get('content', '').lower()
            
            # Search in title and content
            matching_notes = []
            for note in self.notes:
                if query in note.title.lower() or query in note.content.lower():
                    matching_notes.append(note)
            
            if not matching_notes:
                return {'success': True, 'message': f'No notes found for: {query}'}
            
            # Format results
            results = []
            for note in matching_notes:
                results.append(f"{note.title}: {note.content[:100]}")
            
            message = f"Found {len(matching_notes)} notes: " + "; ".join(results)
            
            return {
                'success': True,
                'message': message,
                'notes': [asdict(n) for n in matching_notes]
            }
            
        except Exception as e:
            logger.error(f"Failed to search notes: {e}")
            return {'success': False, 'error': str(e)}


if __name__ == "__main__":
    # Test note system
    logging.basicConfig(level=logging.INFO)
    
    notes = NoteSystem()
    
    # Create note
    result = notes.execute({
        'action': 'create_note',
        'entities': {'content': 'JARVIS is working great!'}
    })
    print(result)
