"""
Command Executor - Handles system-level command execution
"""

import os
import subprocess
import logging
import psutil
import winshell
from pathlib import Path
from typing import Dict, Any, Optional, List
import pyautogui
import ctypes
import screen_brightness_control as sbc

logger = logging.getLogger(__name__)


class CommandExecutor:
    """Executes system commands with trust mode security"""
    
    def __init__(self, automation_config: dict):
        """Initialize command executor"""
        self.config = automation_config
        self.confirm_risky = automation_config.get('confirm_risky_commands', True)
        # Add new allowed operations
        self.allowed_ops = set(automation_config.get('allowed_operations', []) + 
                               ['lock_pc', 'sleep_pc', 'empty_bin', 'check_battery', 'set_brightness'])
        self.restricted_ops = set(automation_config.get('restricted_operations', []))
        
        # Common application paths
        self.app_paths = self._discover_applications()
        
        logger.info("Command executor initialized in trust mode")
    
    def _discover_applications(self) -> Dict[str, str]:
        """Discover installed applications"""
        apps = {}
        
        # Common Windows applications
        common_apps = {
            'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe',
            'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            'notepad': r'C:\Windows\System32\notepad.exe',
            'calculator': r'C:\Windows\System32\calc.exe',
            'explorer': r'C:\Windows\explorer.exe',
            'cmd': r'C:\Windows\System32\cmd.exe',
            'powershell': r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe',
            'vscode': r'C:\Program Files\Microsoft VS Code\Code.exe',
            'spotify': os.path.join(os.getenv('APPDATA', ''), r'Spotify\Spotify.exe'),
        }
        
        # Check which apps exist
        for name, path in common_apps.items():
            if os.path.exists(path):
                apps[name.lower()] = path
        
        logger.info(f"Discovered {len(apps)} applications")
        return apps
    
    def execute(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command based on intent
        
        Args:
            intent: Parsed intent from NLP processor
            
        Returns:
            Result dictionary with success status and message
        """
        action = intent.get('action')
        entities = intent.get('entities', {})
        
        try:
            if action == 'open_app':
                return self._open_application(entities.get('app_name'))
            
            elif action == 'close_app':
                return self._close_application(entities.get('app_name'))
            
            elif action == 'create_file':
                return self._create_file(entities.get('name'))
            
            elif action == 'create_folder':
                return self._create_folder(entities.get('name'))
            
            elif action == 'delete_file':
                return self._delete_file(entities.get('name'))
                
            elif action == 'file_move':
                return self._move_file(entities.get('source'), entities.get('destination'))
                
            elif action == 'lock_pc':
                return self._lock_pc()
                
            elif action == 'sleep_pc':
                return self._sleep_pc(entities.get('mode', 'suspend'))
                
            elif action == 'empty_bin':
                return self._empty_recycle_bin()
                
            elif action == 'check_battery':
                return self._check_battery()
            
            elif action == 'volume_control':
                return self._control_volume(entities)
                
            elif action == 'set_brightness':
                return self._set_brightness(entities)
            
            elif action == 'media_control':
                return self._control_media(entities.get('action'))
            
            elif action == 'system_command':
                return self._execute_system_command(entities)
            
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _open_application(self, app_name: str) -> Dict[str, Any]:
        """Open an application"""
        try:
            app_name = app_name.lower().strip()
            
            # Windows Store Apps Protocol Handlers
            windows_apps = {
                'whatsapp': 'whatsapp://',
                'spotify': 'spotify:',
                'netflix': 'netflix:',
                'calculator': 'calculator:',
                'calendar': 'outlookcal:',
                'camera': 'microsoft.windows.camera:',
                'clock': 'ms-clock:',
                'mail': 'outlookmail:',
                'maps': 'bingmaps:',
                'photos': 'ms-photos:',
                'settings': 'ms-settings:',
                'store': 'ms-windows-store:',
                'weather': 'bingweather:',
            }
            
            # Check protocol handlers first
            if app_name in windows_apps:
                try:
                    os.startfile(windows_apps[app_name])
                    return {'success': True, 'message': f'Opening {app_name}'}
                except Exception:
                    logger.warning(f"Failed to open {app_name} via protocol, trying fallback")
            
            # Check known paths
            if app_name in self.app_paths:
                path = self.app_paths[app_name]
                subprocess.Popen([path])
                return {'success': True, 'message': f'Opening {app_name}'}
            
            # Try start command (finds registered apps)
            try:
                subprocess.run(['start', app_name], shell=True, check=True)
                return {'success': True, 'message': f'Opening {app_name}'}
            except:
                pass
            
            # Try os.startfile as fallback
            try:
                os.startfile(app_name)
                return {'success': True, 'message': f'Opening {app_name}'}
            except:
                return {'success': False, 'error': f'Could not find application: {app_name}'}
                        
        except Exception as e:
            logger.error(f"Failed to open {app_name}: {e}")
            return {'success': False, 'error': f'Failed to open {app_name}'}
    
    def _close_application(self, app_name: str) -> Dict[str, Any]:
        """Close an application"""
        try:
            app_name = app_name.lower().strip()
            closed = False
            
            # Find and terminate process
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if app_name in proc_name or proc_name.startswith(app_name):
                        proc.terminate()
                        closed = True
                        logger.info(f"Closed {proc_name}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if closed:
                return {'success': True, 'message': f'Closed {app_name}'}
            else:
                return {'success': False, 'error': f'{app_name} is not running'}
                
        except Exception as e:
            logger.error(f"Failed to close {app_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_file(self, filename: str) -> Dict[str, Any]:
        """Create a new file"""
        try:
            # Create in Documents folder by default
            docs_path = Path.home() / 'Documents'
            file_path = docs_path / filename
            
            # Create file
            file_path.touch()
            logger.info(f"Created file: {file_path}")
            
            return {'success': True, 'message': f'Created file: {filename}'}
            
        except Exception as e:
            logger.error(f"Failed to create file: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_folder(self, foldername: str) -> Dict[str, Any]:
        """Create a new folder"""
        try:
            # Create in Documents folder by default
            docs_path = Path.home() / 'Documents'
            folder_path = docs_path / foldername
            
            # Create folder
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {folder_path}")
            
            return {'success': True, 'message': f'Created folder: {foldername}'}
            
        except Exception as e:
            logger.error(f"Failed to create folder: {e}")
            return {'success': False, 'error': str(e)}
    
    def _delete_file(self, filename: str) -> Dict[str, Any]:
        """Delete a file (with confirmation for risky operations)"""
        try:
            # This is a restricted operation in trust mode
            if self.confirm_risky:
                logger.warning(f"Delete operation requires confirmation: {filename}")
                return {'success': False, 'error': 'Delete operations require manual confirmation'}
            
            # Move to recycle bin instead of permanent delete
            docs_path = Path.home() / 'Documents'
            file_path = docs_path / filename
            
            if file_path.exists():
                winshell.delete_file(str(file_path), no_confirm=False)
                logger.info(f"Moved to recycle bin: {file_path}")
                return {'success': True, 'message': f'Moved {filename} to recycle bin'}
            else:
                return {'success': False, 'error': f'File not found: {filename}'}
                
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return {'success': False, 'error': str(e)}

    def _move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Move a file to a folder"""
        try:
            import shutil
            
            # Default to Documents if paths are relative
            base_path = Path.home() / 'Documents'
            
            # Resolve Source
            source_path = source
            if not os.path.isabs(source):
                # Try finding in Downloads first, then Documents
                downloads_path = Path.home() / 'Downloads' / source
                docs_path = Path.home() / 'Documents' / source
                
                if downloads_path.exists():
                    source_path = str(downloads_path)
                elif docs_path.exists():
                    source_path = str(docs_path)
                else:
                    return {'success': False, 'error': f'File not found: {source}'}
            
            # Resolve Destination
            dest_folder = destination.lower()
            if 'picture' in dest_folder:
                dest_path = Path.home() / 'Pictures'
            elif 'video' in dest_folder:
                dest_path = Path.home() / 'Videos'
            elif 'music' in dest_folder:
                dest_path = Path.home() / 'Music'
            elif 'document' in dest_folder:
                dest_path = Path.home() / 'Documents'
            elif 'download' in dest_folder:
                dest_path = Path.home() / 'Downloads'
            else:
                dest_path = base_path / destination
                dest_path.mkdir(exist_ok=True)
            
            # Move
            shutil.move(source_path, str(dest_path))
            logger.info(f"Moved {source_path} to {dest_path}")
            
            return {'success': True, 'message': f'Moved {os.path.basename(source_path)} to {destination}'}
            
        except Exception as e:
            logger.error(f"Failed to move file: {e}")
            return {'success': False, 'error': str(e)}
    
    def _control_volume(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Control system volume"""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            if 'level' in entities:
                # Set volume to specific level (0-100)
                level = max(0, min(100, entities['level'])) / 100.0
                volume.SetMasterVolumeLevelScalar(level, None)
                return {'success': True, 'message': f'Volume set to {entities["level"]}%'}
            
            elif 'action' in entities:
                action = entities['action'].lower()
                
                if action == 'mute':
                    volume.SetMute(1, None)
                    return {'success': True, 'message': 'Volume muted'}
                
                elif action == 'unmute':
                    volume.SetMute(0, None)
                    return {'success': True, 'message': 'Volume unmuted'}
                
                elif action == 'up':
                    current = volume.GetMasterVolumeLevelScalar()
                    new_level = min(1.0, current + 0.1)
                    volume.SetMasterVolumeLevelScalar(new_level, None)
                    return {'success': True, 'message': 'Volume increased'}
                
                elif action == 'down':
                    current = volume.GetMasterVolumeLevelScalar()
                    new_level = max(0.0, current - 0.1)
                    volume.SetMasterVolumeLevelScalar(new_level, None)
                    return {'success': True, 'message': 'Volume decreased'}
            
            return {'success': False, 'error': 'Invalid volume command'}
            
        except Exception as e:
            logger.error(f"Volume control failed: {e}")
            return {'success': False, 'error': 'Volume control not available'}
    
    def _control_media(self, action: str) -> Dict[str, Any]:
        """Control media playback"""
        try:
            # Use keyboard shortcuts for media control
            media_keys = {
                'play': 'playpause',
                'pause': 'playpause',
                'stop': 'stop',
                'next': 'nexttrack',
                'previous': 'prevtrack'
            }
            
            key = media_keys.get(action.lower())
            if key:
                pyautogui.press(key)
                return {'success': True, 'message': f'Media {action}'}
            else:
                return {'success': False, 'error': f'Unknown media action: {action}'}
                
        except Exception as e:
            logger.error(f"Media control failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _lock_pc(self) -> Dict[str, Any]:
        """Lock the workstation"""
        try:
            ctypes.windll.user32.LockWorkStation()
            return {'success': True, 'message': 'Workstation locked'}
        except Exception as e:
            logger.error(f"Failed to lock PC: {e}")
            return {'success': False, 'error': str(e)}

    def _sleep_pc(self, mode: str = 'suspend') -> Dict[str, Any]:
        """Put PC to sleep"""
        try:
            if mode == 'hibernate':
                os.system("rundll32.exe powrprof.dll,SetSuspendState 1,1,0")
                return {'success': True, 'message': 'Hibernating system'}
            else:
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                return {'success': True, 'message': 'Putting system to sleep'}
        except Exception as e:
            logger.error(f"Failed to sleep PC: {e}")
            return {'success': False, 'error': str(e)}

    def _empty_recycle_bin(self) -> Dict[str, Any]:
        """Empty Windows Recycle Bin"""
        try:
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            return {'success': True, 'message': 'Recycle bin emptied'}
        except Exception as e:
            logger.error(f"Failed to empty recycle bin: {e}")
            return {'success': False, 'error': str(e)}
            
    def _check_battery(self) -> Dict[str, Any]:
        """Check battery status"""
        try:
            battery = psutil.sensors_battery()
            if not battery:
                return {'success': True, 'message': 'System is running on AC power (no battery detected)'}
                
            plugged = battery.power_plugged
            percent = battery.percent
            
            status = "plugged in" if plugged else "running on battery"
            
            if not plugged and battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                hours = battery.secsleft // 3600
                mins = (battery.secsleft % 3600) // 60
                time_left = f", with about {hours}h {mins}m remaining"
            else:
                time_left = ""
                
            return {'success': True, 'message': f'Battery is at {percent}% and {status}{time_left}'}
        except Exception as e:
            logger.error(f"Failed to check battery: {e}")
            return {'success': False, 'error': str(e)}

    def _set_brightness(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Control screen brightness"""
        try:
            current = sbc.get_brightness()
            current = current[0] if isinstance(current, list) else current
            
            if 'level' in entities:
                level = max(0, min(100, int(entities['level'])))
                sbc.set_brightness(level)
                return {'success': True, 'message': f'Brightness set to {level}%'}
                
            elif 'action' in entities:
                action = entities['action'].lower()
                if action == 'up':
                    new_level = min(100, current + 10)
                    sbc.set_brightness(new_level)
                    return {'success': True, 'message': 'Brightness increased'}
                elif action == 'down':
                    new_level = max(0, current - 10)
                    sbc.set_brightness(new_level)
                    return {'success': True, 'message': 'Brightness decreased'}
            
            return {'success': False, 'error': 'Invalid brightness command'}
        except Exception as e:
            logger.error(f"Failed to set brightness: {e}")
            return {'success': False, 'error': 'Brightness control not available'}

    def _execute_system_command(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute system command (with restrictions)"""
        command = entities.get('command', '')
        
        # Check if command is restricted
        if any(restricted in command.lower() for restricted in self.restricted_ops):
            logger.warning(f"Blocked restricted command: {command}")
            return {'success': False, 'error': 'This command is restricted for safety'}
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return {'success': True, 'message': 'Command executed', 'output': result.stdout}
            else:
                return {'success': False, 'error': result.stderr}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timed out'}
        except Exception as e:
            logger.error(f"System command failed: {e}")
            return {'success': False, 'error': str(e)}


if __name__ == "__main__":
    # Test command executor
    logging.basicConfig(level=logging.INFO)
    
    config = {
        'confirm_risky_commands': True,
        'allowed_operations': ['open_app', 'create_file', 'volume_control'],
        'restricted_operations': ['shutdown', 'restart']
    }
    
    executor = CommandExecutor(config)
    
    # Test opening an app
    result = executor.execute({
        'action': 'open_app',
        'entities': {'app_name': 'notepad'}
    })
    print(result)
