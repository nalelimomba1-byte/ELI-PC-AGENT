import customtkinter as ctk
import threading
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DesktopApp(ctk.CTk):
    def __init__(self, core_system):
        super().__init__()
        
        self.core = core_system
        self.title("ANNY - Local Assistant")
        self.geometry("400x600")
        
        # Configure Grid
        self.grid_rowconfigure(1, weight=1) # Chat expands
        self.grid_columnconfigure(0, weight=1)
        
        # 1. Header / Status
        self.status_frame = ctk.CTkFrame(self, height=40, corner_radius=0)
        self.status_frame.grid(row=0, column=0, sticky="ew")
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="🟢 Ready", text_color="gray")
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # 2. Chat Area
        self.chat_box = ctk.CTkTextbox(self, state="disabled", wrap="word")
        self.chat_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # 3. Input Area
        self.input_frame = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.input_frame.grid(row=2, column=0, sticky="ew")
        
        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Type a message...")
        self.entry.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.entry.bind("<Return>", self.send_message)
        
        self.send_btn = ctk.CTkButton(self.input_frame, text="➤", width=40, command=self.send_message)
        self.send_btn.pack(side="right", padx=10, pady=10)

        # Connect callbacks
        if self.core:
             self.core.register_ui_callback(self.add_message)
             self.core.register_status_callback(self.update_status)

        self.add_message("System", "Welcome to ANNY. Core initialized.")

    def send_message(self, event=None):
        text = self.entry.get()
        if not text:
            return
            
        self.add_message("User", text)
        self.entry.delete(0, "end")
        
        # Send to core in background
        if self.core:
            threading.Thread(target=self.core.handle_text_input, args=(text,), daemon=True).start()

    def add_message(self, sender, message):
        """Thread-safe UI update"""
        # Scheduled for main thread
        self.after(0, self._add_message_internal, sender, message)
        
    def _add_message_internal(self, sender, message):
        timestamp = datetime.now().strftime("%H:%M")
        
        self.chat_box.configure(state="normal")
        
        if sender == "User":
            prefix = f"👤 {sender} [{timestamp}]:\n"
            tag = "user"
        elif sender == "System":
             prefix = f"⚙️ {sender}:\n"
             tag = "system"
        else:
            prefix = f"🤖 {sender} [{timestamp}]:\n"
            tag = "bot"
            
        self.chat_box.insert("end", prefix + f"{message}\n\n")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")
        
    def update_status(self, status_text, color="gray"):
        self.after(0, lambda: self.status_label.configure(text=status_text, text_color=color))

    def on_closing(self):
        if self.core:
            self.core.stop()
        self.destroy()
