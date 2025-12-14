"""
Scheduler - Manages events, reminders, and scheduled tasks
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Event/Reminder data structure"""
    id: str
    name: str
    description: str = ""
    event_time: str = ""
    created_at: str = ""
    completed: bool = False
    recurring: bool = False
    recurrence_pattern: Optional[str] = None  # daily, weekly, monthly
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class Scheduler:
    """Manages scheduled events and reminders"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize scheduler"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.events_file = self.data_dir / "events.json"
        self.events: List[Event] = []
        
        self._load_events()
        logger.info(f"Scheduler initialized with {len(self.events)} events")
    
    def _load_events(self):
        """Load events from file"""
        try:
            if self.events_file.exists():
                with open(self.events_file, 'r') as f:
                    data = json.load(f)
                    self.events = [Event(**event) for event in data]
                logger.info(f"Loaded {len(self.events)} events")
        except Exception as e:
            logger.error(f"Failed to load events: {e}")
            self.events = []
    
    def _save_events(self):
        """Save events to file"""
        try:
            with open(self.events_file, 'w') as f:
                json.dump([asdict(event) for event in self.events], f, indent=2)
            logger.info("Events saved")
        except Exception as e:
            logger.error(f"Failed to save events: {e}")
    
    def execute(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scheduling command"""
        action = intent.get('action')
        entities = intent.get('entities', {})
        
        try:
            if action == 'schedule_event':
                return self._schedule_event(entities)
            
            elif action == 'set_reminder':
                return self._set_reminder(entities)
            
            else:
                return {'success': False, 'error': f'Unknown scheduler action: {action}'}
                
        except Exception as e:
            logger.error(f"Scheduler operation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _schedule_event(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule an event"""
        try:
            event_name = entities.get('event_name', 'Untitled Event')
            event_time = entities.get('datetime', '')
            
            # Parse datetime
            parsed_time = self._parse_datetime(event_time)
            
            event = Event(
                id=str(uuid.uuid4()),
                name=event_name,
                event_time=parsed_time
            )
            
            self.events.append(event)
            self._save_events()
            
            logger.info(f"Scheduled event: {event_name} at {parsed_time}")
            return {'success': True, 'message': f'Event scheduled: {event_name}'}
            
        except Exception as e:
            logger.error(f"Failed to schedule event: {e}")
            return {'success': False, 'error': str(e)}
    
    def _set_reminder(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Set a reminder"""
        try:
            reminder_text = entities.get('reminder_text', 'Reminder')
            reminder_time = entities.get('datetime', '')
            
            # Parse datetime
            parsed_time = self._parse_datetime(reminder_time)
            
            event = Event(
                id=str(uuid.uuid4()),
                name=f"Reminder: {reminder_text}",
                event_time=parsed_time
            )
            
            self.events.append(event)
            self._save_events()
            
            logger.info(f"Set reminder: {reminder_text} at {parsed_time}")
            return {'success': True, 'message': f'Reminder set: {reminder_text}'}
            
        except Exception as e:
            logger.error(f"Failed to set reminder: {e}")
            return {'success': False, 'error': str(e)}
    
    def _parse_datetime(self, time_str: str) -> str:
        """Parse natural language datetime"""
        if not time_str:
            return datetime.now().isoformat()
        
        time_str = time_str.lower().strip()
        now = datetime.now()
        
        # Handle common patterns
        if time_str == 'tomorrow':
            target = now + timedelta(days=1)
            return target.replace(hour=9, minute=0).isoformat()
        
        elif time_str == 'today':
            return now.isoformat()
        
        elif time_str == 'tonight':
            return now.replace(hour=20, minute=0).isoformat()
        
        elif 'hour' in time_str:
            # Extract number of hours
            import re
            match = re.search(r'(\d+)\s*hour', time_str)
            if match:
                hours = int(match.group(1))
                target = now + timedelta(hours=hours)
                return target.isoformat()
        
        elif 'minute' in time_str:
            # Extract number of minutes
            import re
            match = re.search(r'(\d+)\s*minute', time_str)
            if match:
                minutes = int(match.group(1))
                target = now + timedelta(minutes=minutes)
                return target.isoformat()
        
        elif ':' in time_str:
            # Parse time like "5:30pm"
            import re
            match = re.search(r'(\d{1,2}):(\d{2})\s*([ap]m)?', time_str)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2))
                meridiem = match.group(3)
                
                if meridiem == 'pm' and hour < 12:
                    hour += 12
                elif meridiem == 'am' and hour == 12:
                    hour = 0
                
                target = now.replace(hour=hour, minute=minute, second=0)
                
                # If time has passed today, schedule for tomorrow
                if target < now:
                    target += timedelta(days=1)
                
                return target.isoformat()
        
        # Default: 1 hour from now
        return (now + timedelta(hours=1)).isoformat()
    
    def get_pending_tasks(self) -> List[Event]:
        """Get events that are due now"""
        now = datetime.now()
        pending = []
        
        for event in self.events:
            if event.completed:
                continue
            
            try:
                event_time = datetime.fromisoformat(event.event_time)
                
                # Check if event is due (within 1 minute)
                if abs((event_time - now).total_seconds()) < 60:
                    pending.append(asdict(event))
                    event.completed = True
            except:
                continue
        
        if pending:
            self._save_events()
        
        return pending


if __name__ == "__main__":
    # Test scheduler
    logging.basicConfig(level=logging.INFO)
    
    scheduler = Scheduler()
    
    # Set reminder
    result = scheduler.execute({
        'action': 'set_reminder',
        'entities': {'reminder_text': 'Test JARVIS', 'datetime': '5 minutes'}
    })
    print(result)
