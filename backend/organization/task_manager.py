"""
Task Manager - Manages tasks and to-do lists
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
class Task:
    """Task data structure"""
    id: str
    name: str
    description: str = ""
    created_at: str = ""
    due_date: Optional[str] = None
    completed: bool = False
    completed_at: Optional[str] = None
    priority: str = "medium"  # low, medium, high
    tags: List[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if self.tags is None:
            self.tags = []


class TaskManager:
    """Manages tasks and to-do lists"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize task manager"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.tasks_file = self.data_dir / "tasks.json"
        self.tasks: List[Task] = []
        
        self._load_tasks()
        logger.info(f"Task manager initialized with {len(self.tasks)} tasks")
    
    def _load_tasks(self):
        """Load tasks from file"""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task(**task) for task in data]
                logger.info(f"Loaded {len(self.tasks)} tasks")
        except Exception as e:
            logger.error(f"Failed to load tasks: {e}")
            self.tasks = []
    
    def _save_tasks(self):
        """Save tasks to file"""
        try:
            with open(self.tasks_file, 'w') as f:
                json.dump([asdict(task) for task in self.tasks], f, indent=2)
            logger.info("Tasks saved")
        except Exception as e:
            logger.error(f"Failed to save tasks: {e}")
    
    def execute(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task management command"""
        action = intent.get('action')
        entities = intent.get('entities', {})
        
        try:
            if action == 'create_task':
                return self._create_task(entities)
            
            elif action == 'list_tasks':
                return self._list_tasks(entities)
            
            elif action == 'complete_task':
                return self._complete_task(entities)
            
            else:
                return {'success': False, 'error': f'Unknown task action: {action}'}
                
        except Exception as e:
            logger.error(f"Task operation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_task(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        try:
            task_name = entities.get('task_name', 'Untitled Task')
            due_date = entities.get('due_date')
            
            task = Task(
                id=str(uuid.uuid4()),
                name=task_name,
                due_date=due_date
            )
            
            self.tasks.append(task)
            self._save_tasks()
            
            logger.info(f"Created task: {task_name}")
            return {'success': True, 'message': f'Task created: {task_name}'}
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return {'success': False, 'error': str(e)}
    
    def _list_tasks(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """List all tasks"""
        try:
            # Filter incomplete tasks by default
            incomplete_tasks = [t for t in self.tasks if not t.completed]
            
            if not incomplete_tasks:
                return {'success': True, 'message': 'You have no pending tasks'}
            
            # Format task list
            task_list = []
            for i, task in enumerate(incomplete_tasks, 1):
                due = f" (due: {task.due_date})" if task.due_date else ""
                task_list.append(f"{i}. {task.name}{due}")
            
            message = f"You have {len(incomplete_tasks)} pending tasks: " + ", ".join(task_list)
            
            return {
                'success': True,
                'message': message,
                'tasks': [asdict(t) for t in incomplete_tasks]
            }
            
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            return {'success': False, 'error': str(e)}
    
    def _complete_task(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Mark a task as complete"""
        try:
            task_name = entities.get('task_name', '')
            
            # Find task by name (partial match)
            matching_tasks = [t for t in self.tasks if task_name.lower() in t.name.lower() and not t.completed]
            
            if not matching_tasks:
                return {'success': False, 'error': f'Task not found: {task_name}'}
            
            # Complete the first matching task
            task = matching_tasks[0]
            task.completed = True
            task.completed_at = datetime.now().isoformat()
            
            self._save_tasks()
            
            logger.info(f"Completed task: {task.name}")
            return {'success': True, 'message': f'Task completed: {task.name}'}
            
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        try:
            self.tasks = [t for t in self.tasks if t.id != task_id]
            self._save_tasks()
            return True
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            return False


if __name__ == "__main__":
    # Test task manager
    logging.basicConfig(level=logging.INFO)
    
    manager = TaskManager()
    
    # Create task
    result = manager.execute({
        'action': 'create_task',
        'entities': {'task_name': 'Test JARVIS system', 'due_date': 'tomorrow'}
    })
    print(result)
    
    # List tasks
    result = manager.execute({
        'action': 'list_tasks',
        'entities': {}
    })
    print(result)
