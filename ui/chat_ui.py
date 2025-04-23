import torch
from llama_cpp import Llama
import sys
import time
from typing import List, Dict
import os
import re
import tkinter as tk
from tkinter import scrolledtext, ttk
from datetime import datetime
import threading

# Dark theme colors - updated to match screenshot
DARK_BG = "#2b2b2b"  # Main background
DARK_FG = "#e0e0e0"  # Main text color
DARK_SECONDARY = "#333333"  # Secondary background
DARK_ACCENT = "#4a90e2"  # Accent color
DARK_USER_TEXT = "#4a90e2"  # User message text color
DARK_ASSISTANT_TEXT = "#27ae60"  # Assistant message text color
DARK_TYPING = "#888888"  # Typing indicator
DARK_INPUT_BG = "#333333"  # Input field background
DARK_INPUT_FG = "#ffffff"  # Input field text
HEADER_BG = "#000000"  # Header background

class JackSparrowChat:
    def __init__(self):
        self.llm = None
        self.conversation_history: List[Dict] = []
        self.max_seq_length = 2048
        self.last_response = ""
        
    def initialize_model(self):
        """Initialize the model."""
        try:
            print("Initializing model... This may take a moment.")
            
            # Initialize llama.cpp model
            self.llm = Llama    (
                model_path="C:\\Users\\Emeric\\.cache\\huggingface\\hub\\models--Devwa--jackSparrow\\snapshots\\54a555e116e1b87d707362cd816b552d32f5895d\\unsloth.Q4_K_M.gguf",
                n_ctx=self.max_seq_length,
                n_threads=4,  # Adjust based on your CPU
                n_gpu_layers=0  # CPU only
            )
            
            print("Model initialized successfully!")
            return True
        except Exception as e:
            print(f"Error initializing model: {e}")
            return False

    def clean_response(self, response: str) -> str:
        """Clean up the response by removing stage directions and multiple responses."""
        # Split by "Jack Sparrow:" to get only the first response
        parts = response.split('Jack Sparrow:')
        if parts:
            response = parts[0].strip()
        return response.strip()

    def format_prompt(self, user_input: str) -> str:
        """Format the prompt for the model."""
        # System message to guide the model's behavior
        system_prompt = """You are Captain Jack Sparrow from Pirates of the Caribbean. 
You are witty, clever, and always have a plan. You speak in a distinctive pirate manner.
You should:
1. Stay in character as Jack Sparrow
2. Be concise and avoid repeating yourself
3. Use pirate-like expressions (e.g., "Savvy?", "Aye")
4. Never break character or acknowledge being an AI
5. Keep responses focused on the current conversation
6. Do not include stage directions or multiple responses
7. Speak naturally as if in a conversation

Current conversation:"""

        # Build context from conversation history
        context = system_prompt + "\n"
        for msg in self.conversation_history[-3:]:  # Keep last 3 messages for context
            if msg["role"] == "user":
                context += f"Human: {msg['content']}\n"
            else:
                context += f"Jack: {msg['content']}\n"
        
        # Add current user input
        context += f"Human: {user_input}\nJack:"
        return context

    def is_repetitive(self, response: str) -> bool:
        """Check if the response is repetitive."""
        if not self.last_response:
            return False
        
        # Clean both responses before comparison
        clean_response = self.clean_response(response)
        clean_last = self.clean_response(self.last_response)
        
        # Check if the response is too similar to the last one
        response_words = set(clean_response.lower().split())
        last_words = set(clean_last.lower().split())
        similarity = len(response_words.intersection(last_words)) / len(response_words)
        
        return similarity > 0.7  # If more than 70% of words are the same

    def generate_response(self, user_input: str) -> str:
        """Generate a response from the model."""
        if not self.llm:
            return "Model not initialized. Please check your setup."

        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})

        try:
            # Format the prompt
            prompt = self.format_prompt(user_input)
            
            # Generate response
            output = self.llm(
                prompt,
                max_tokens=100,  # Reduced to prevent multiple responses
                temperature=0.8,
                top_p=0.9,
                stop=["Human:", "\n\n", "Jack:", "Jack Sparrow:"],  # Stop at next speaker or double newline
                stream=False
            )
            
            # Get the response
            response = output["choices"][0]["text"]
            
            # Clean up the response
            response = self.clean_response(response)
            
            # Check for repetition
            if self.is_repetitive(response):
                return self.generate_response(user_input)  # Try again
            
            # Update last response and add to history
            self.last_response = response
            self.conversation_history.append({"role": "assistant", "content": response})
            return response

        except Exception as e:
            return f"Error generating response: {e}"

class ChatGUI:
    def __init__(self, chat_model):
        self.chat_model = chat_model
        self.root = tk.Tk()
        self.root.title("Jack Sparrow Chat")
        self.root.geometry("800x600")
        self.root.configure(bg=DARK_BG)
        
        # Configure style for rounded corners
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background=DARK_ACCENT)
        self.style.configure("TEntry", padding=6)
        self.style.configure("Header.TFrame", background=HEADER_BG)
        self.style.configure("Main.TFrame", background=DARK_BG)
        
        # Set window icon
        self.root.iconbitmap("jack_icon.ico") if os.path.exists("jack_icon.ico") else None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with dark background
        main_frame = ttk.Frame(self.root, padding="10", style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header - just the title text without spanning background
        header_frame = ttk.Frame(main_frame, style="Main.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create a frame just for the title with specific background
        title_container = tk.Frame(header_frame, bg=DARK_SECONDARY, padx=10, pady=5)
        title_container.pack(side=tk.LEFT)
        
        title_label = tk.Label(
            title_container,
            text="Captain Jack Sparrow",
            font=("Montserrat", 16, "bold"),
            foreground=DARK_FG,
            background=DARK_SECONDARY
        )
        title_label.pack()
        
        # Chat history
        chat_frame = tk.Frame(main_frame, bg=DARK_BG)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.chat_history = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=60,
            height=20,
            font=("Verdana", 12),
            bg=DARK_SECONDARY,
            fg=DARK_FG,
            relief="flat",
            padx=10,
            pady=10,
            insertbackground=DARK_FG,
            selectbackground=DARK_ACCENT,
            selectforeground=DARK_FG,
            borderwidth=5
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Input area with rounded corners
        input_frame = tk.Frame(main_frame, bg=DARK_BG)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Custom Entry widget with rounded corners
        self.message_input = tk.Entry(
            input_frame,
            font=("Verdana", 10),
            bg=DARK_INPUT_BG,
            fg=DARK_INPUT_FG,
            insertbackground=DARK_FG,
            relief="flat",
            borderwidth=5,
            highlightthickness=1,
            highlightbackground=DARK_SECONDARY,
            highlightcolor=DARK_ACCENT
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=5)
        self.message_input.bind("<Return>", self.send_message)
        
        # Custom Button with rounded corners
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg=DARK_ACCENT,
            fg=DARK_FG,
            relief="raised",
            borderwidth=0,
            padx=15,
            pady=5,
            font=("Montserrat", 12, "bold"),
            activebackground=DARK_ACCENT,
            activeforeground=DARK_FG
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Clear button with rounded corners
        clear_button = tk.Button(
            input_frame,
            text="Clear Chat",
            command=self.clear_chat,
            bg=DARK_SECONDARY,
            fg=DARK_FG,
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=5,
            font=("Verdana", 10),
            activebackground=DARK_SECONDARY,
            activeforeground=DARK_FG
        )
        clear_button.pack(side=tk.RIGHT, padx=10)
        
        # Add welcome message
        self.add_message("Jack Sparrow", "Ahoy there! Captain Jack Sparrow at your service. What brings you to my humble presence?")
        
    def add_message(self, sender: str, message: str):
        self.chat_history.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")
        
        # Format message without backgrounds, just colored text
        if sender == "You":
            self.chat_history.insert(tk.END, f"\n[{timestamp}] ", "timestamp")
            self.chat_history.insert(tk.END, "You: ", "user_name")
            self.chat_history.insert(tk.END, f"{message}\n", "user_message")
        else:
            self.chat_history.insert(tk.END, f"\n[{timestamp}] ", "timestamp")
            self.chat_history.insert(tk.END, "Jack Sparrow: ", "assistant_name")
            self.chat_history.insert(tk.END, f"{message}\n", "assistant_message")
        
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)
        
        # Configure tags with colors but no backgrounds
        self.chat_history.tag_configure("timestamp", foreground="#888888")
        self.chat_history.tag_configure("user_name", foreground=DARK_USER_TEXT, font=("Verdana", 12, "bold"))
        self.chat_history.tag_configure("user_message", foreground=DARK_USER_TEXT)
        self.chat_history.tag_configure("assistant_name", foreground=DARK_ASSISTANT_TEXT, font=("Verdana", 12, "bold"))
        self.chat_history.tag_configure("assistant_message", foreground=DARK_ASSISTANT_TEXT)
    
    def show_typing_indicator(self):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, "\nJack Sparrow is typing...\n", "typing")
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.tag_configure("typing", foreground=DARK_TYPING, font=("Verdana", 10, "italic"))
    
    def remove_typing_indicator(self):
        """Remove the typing indicator."""
        self.chat_history.config(state=tk.NORMAL)
        # Remove the last two lines (typing indicator)
        self.chat_history.delete("end-2l linestart", "end")
        self.chat_history.config(state=tk.DISABLED)
    
    def generate_response_thread(self, message: str):
        """Generate response in a separate thread."""
        # Disable input while generating
        self.message_input.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        
        # Show typing indicator
        self.show_typing_indicator()
        
        # Generate response
        response = self.chat_model.generate_response(message)
        
        # Remove typing indicator and add response
        self.remove_typing_indicator()
        self.add_message("Jack Sparrow", response)
        
        # Re-enable input
        self.message_input.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)
        self.message_input.focus()
    
    def send_message(self, event=None):
        message = self.message_input.get().strip()
        if message:
            # Clear input immediately
            self.message_input.delete(0, tk.END)
            
            # Add user message to chat immediately
            self.add_message("You", message)
            
            # Start response generation in a separate thread
            threading.Thread(
                target=self.generate_response_thread,
                args=(message,),
                daemon=True
            ).start()
    
    def clear_chat(self):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.delete(1.0, tk.END)
        self.chat_history.config(state=tk.DISABLED)
        self.chat_model.conversation_history = []
        self.chat_model.last_response = ""
        self.add_message("Jack Sparrow", "Ahoy there! Captain Jack Sparrow at your service. What brings you to my humble presence?")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    chat = JackSparrowChat()
    if chat.initialize_model():
        gui = ChatGUI(chat)
        gui.run()
    else:
        print("Failed to initialize the model. Exiting...") 