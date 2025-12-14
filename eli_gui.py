"""
ELI Native GUI - Desktop application with particle sphere
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import math
import random
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.eli_core import EliCore

class Particle:
    def __init__(self, index, total, radius):
        self.angle = (index / total) * math.pi * 2
        self.base_radius = radius
        self.radius = radius
        self.x = 0
        self.y = 0
        self.size = 3 + random.random() * 2
        self.speed = 0.002 + random.random() * 0.003
        self.offset = random.random() * math.pi * 2
        self.pulse_speed = 0.03 + random.random() * 0.02
        self.pulse_offset = random.random() * math.pi * 2
        
    def update(self, time_val, audio_level):
        self.angle += self.speed
        pulse = math.sin(time_val * self.pulse_speed + self.pulse_offset) * 8
        audio_reaction = audio_level * 30
        self.radius = self.base_radius + pulse + audio_reaction
        self.x = math.cos(self.angle) * self.radius
        self.y = math.sin(self.angle) * self.radius

class EliGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ELI - Enhanced Learning Intelligence")
        self.root.geometry("800x900")
        self.root.configure(bg='#000000')
        
        # Initialize ELI backend
        self.eli = None
        self.backend_thread = None
        self.running = True
        
        # Particle system
        self.particles = []
        self.particle_count = 50
        self.particle_radius = 100
        self.time_val = 0
        self.audio_level = 0
        self.is_listening = False
        
        # Initialize particles
        for i in range(self.particle_count):
            self.particles.append(Particle(i, self.particle_count, self.particle_radius))
        
        self.setup_ui()
        self.start_backend()
        self.animate_particles()
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#000000')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(
            main_frame,
            text="ELI",
            font=('Arial', 48, 'bold'),
            fg='#ffffff',
            bg='#000000'
        )
        title.pack(pady=(0, 5))
        
        subtitle = tk.Label(
            main_frame,
            text="Enhanced Learning Intelligence",
            font=('Arial', 12),
            fg='#666666',
            bg='#000000'
        )
        subtitle.pack(pady=(0, 20))
        
        # Particle canvas
        self.canvas = tk.Canvas(
            main_frame,
            width=300,
            height=300,
            bg='#000000',
            highlightthickness=0
        )
        self.canvas.pack(pady=20)
        self.canvas.bind('<Button-1>', self.toggle_listening)
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="Ready",
            font=('Arial', 11),
            fg='#666666',
            bg='#000000'
        )
        self.status_label.pack(pady=10)
        
        # Conversation area
        conv_frame = tk.Frame(main_frame, bg='#000000')
        conv_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        self.conversation = scrolledtext.ScrolledText(
            conv_frame,
            wrap=tk.WORD,
            font=('Arial', 11),
            bg='#1a1a1a',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief=tk.FLAT,
            padx=15,
            pady=15,
            height=10
        )
        self.conversation.pack(fill=tk.BOTH, expand=True)
        self.conversation.config(state=tk.DISABLED)
        
        # Input area
        input_frame = tk.Frame(main_frame, bg='#000000')
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.input_field = tk.Entry(
            input_frame,
            font=('Arial', 12),
            bg='#1a1a1a',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief=tk.FLAT,
            bd=10
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.input_field.bind('<Return>', self.send_command)
        
        send_btn = tk.Button(
            input_frame,
            text="Send",
            font=('Arial', 11, 'bold'),
            bg='#ffffff',
            fg='#000000',
            relief=tk.FLAT,
            padx=20,
            command=self.send_command
        )
        send_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
    def start_backend(self):
        """Start ELI backend in separate thread"""
        def run_backend():
            try:
                self.add_message("System", "Initializing ELI backend...")
                self.eli = EliCore()
                self.add_message("System", "✅ ELI is ready!")
                self.status_label.config(text="Listening...", fg='#ffffff')
            except Exception as e:
                self.add_message("System", f"❌ Error: {str(e)}")
        
        self.backend_thread = threading.Thread(target=run_backend, daemon=True)
        self.backend_thread.start()
    
    def toggle_listening(self, event=None):
        """Toggle listening state"""
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.status_label.config(text="Listening...", fg='#ffffff')
            self.audio_level = 0.5  # Simulate audio for visual effect
        else:
            self.status_label.config(text="Click sphere to activate", fg='#666666')
            self.audio_level = 0
    
    def animate_particles(self):
        """Animate particle sphere"""
        if not self.running:
            return
            
        self.canvas.delete('all')
        center_x = 150
        center_y = 150
        
        # Update particles
        for particle in self.particles:
            particle.update(self.time_val, self.audio_level)
            
            x = center_x + particle.x
            y = center_y + particle.y
            
            # Draw particle
            brightness = int(200 + self.audio_level * 55)
            color = f'#{brightness:02x}{brightness:02x}{brightness:02x}'
            
            self.canvas.create_oval(
                x - particle.size, y - particle.size,
                x + particle.size, y + particle.size,
                fill=color, outline=''
            )
        
        # Draw connections
        for i, p1 in enumerate(self.particles):
            x1 = center_x + p1.x
            y1 = center_y + p1.y
            
            for j, p2 in enumerate(self.particles):
                if j <= i:
                    continue
                    
                x2 = center_x + p2.x
                y2 = center_y + p2.y
                distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                
                if distance < 60:
                    opacity = int((1 - distance / 60) * 50 * (1 + self.audio_level))
                    color = f'#{opacity:02x}{opacity:02x}{opacity:02x}'
                    self.canvas.create_line(x1, y1, x2, y2, fill=color, width=1)
        
        # Center glow
        glow_size = int(15 + self.audio_level * 40)
        glow_opacity = int(50 + self.audio_level * 100)
        glow_color = f'#{glow_opacity:02x}{glow_opacity:02x}{glow_opacity:02x}'
        self.canvas.create_oval(
            center_x - glow_size, center_y - glow_size,
            center_x + glow_size, center_y + glow_size,
            fill=glow_color, outline=''
        )
        
        self.time_val += 0.1
        
        # Decay audio level
        if self.audio_level > 0:
            self.audio_level *= 0.95
        
        self.root.after(50, self.animate_particles)
    
    def add_message(self, role, content):
        """Add message to conversation"""
        self.conversation.config(state=tk.NORMAL)
        
        # Add role label
        self.conversation.insert(tk.END, f"{role}\n", 'role')
        self.conversation.tag_config('role', foreground='#666666', font=('Arial', 9, 'bold'))
        
        # Add content
        self.conversation.insert(tk.END, f"{content}\n\n", 'content')
        self.conversation.tag_config('content', foreground='#ffffff', font=('Arial', 11))
        
        self.conversation.see(tk.END)
        self.conversation.config(state=tk.DISABLED)
    
    def send_command(self, event=None):
        """Send command to ELI"""
        command = self.input_field.get().strip()
        if not command:
            return
        
        self.input_field.delete(0, tk.END)
        self.add_message("You", command)
        
        # Simulate audio reaction
        self.audio_level = 0.8
        self.status_label.config(text="Thinking...", fg='#ffffff')
        
        # Process command in background
        def process():
            try:
                if not self.eli:
                    response = "Backend still initializing..."
                else:
                    # Process through NLP
                    intent_data = self.eli.nlp_processor.process(command)
                    
                    # Execute based on intent
                    if intent_data['intent'] == 'open_app':
                        result = self.eli.command_executor.execute(intent_data)
                        response = result.get('response', 'Command executed')
                    elif intent_data['intent'] in ['create_task', 'list_tasks', 'complete_task']:
                        result = self.eli.task_manager.execute(intent_data)
                        response = result.get('response', 'Task updated')
                    else:
                        response = self.eli.nlp_processor.generate_response(command)
                
                self.root.after(0, lambda: self.add_message("ELI", response))
                self.root.after(0, lambda: self.status_label.config(text="Listening...", fg='#ffffff'))
            except Exception as e:
                self.root.after(0, lambda: self.add_message("ELI", f"Error: {str(e)}"))
                self.root.after(0, lambda: self.status_label.config(text="Ready", fg='#666666'))
        
        threading.Thread(target=process, daemon=True).start()
    
    def on_closing(self):
        """Handle window closing"""
        self.running = False
        if self.eli:
            self.eli.stop()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = EliGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
