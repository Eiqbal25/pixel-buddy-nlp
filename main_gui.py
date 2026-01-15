"""
PIXEL BUDDY - GUI Application
Beautiful football-themed chat interface
RUN THIS FILE!
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import customtkinter as ctk
from threading import Thread
import yaml
from datetime import datetime
import os
import sys
import time

# Import our modules
from stt_improved import ImprovedSpeechToText
from nlp_processor import NLPProcessor
from tts import TextToSpeech
from metrics_logger import MetricsLogger

# Set appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

class PixelBuddyGUI:
    def tts_worker(self):
        import pyttsx3

        engine = pyttsx3.init()
        engine.setProperty('rate', self.config['tts']['rate'])
        engine.setProperty('volume', self.config['tts']['volume'])

        while True:
            text = self.tts_queue.get()
            if text is None:
                break  # shutdown signal

            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print("TTS Worker Error:", e)

            self.root.after(0, self.after_speaking)

    def __init__(self):
        """Initialize PIXEL BUDDY GUI"""
        import queue

        self.tts_queue = queue.Queue()
        self.tts_thread = Thread(target=self.tts_worker, daemon=True)
        self.tts_thread.start()
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("⚽ PIXEL BUDDY - Soccer Rules Assistant")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Load configuration
        with open('config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components (in background)
        self.stt = None
        self.nlp = None
        self.tts = None
        self.logger = MetricsLogger()
        self.is_listening = False
        self.is_processing = False
        self.is_speaking = False
        self.is_closing = False
        self.skip_current = False  # NEW: Flag to skip current response
        
        # Setup GUI
        self.setup_gui()
        
        # Initialize AI components in background
        self.init_status.set("⚙️ Loading AI components...")
        Thread(target=self.initialize_components, daemon=True).start()

    
    def setup_gui(self):
        """Setup the GUI layout"""
        
        # ===== HEADER =====
        header_frame = ctk.CTkFrame(self.root, fg_color="#1B245E", height=80)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚽ PIXEL BUDDY",
            font=("Arial Black", 28, "bold"),
            text_color="white"
        )
        title_label.pack(pady=10)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Your Soccer Rules Expert",
            font=("Arial", 14),
            text_color="#AFA5D6"
        )
        subtitle_label.pack()
        
        # ===== STATUS BAR =====
        status_frame = ctk.CTkFrame(self.root, fg_color="#E8EBF5", height=40)
        status_frame.pack(fill="x", padx=0, pady=0)
        status_frame.pack_propagate(False)
        
        self.init_status = tk.StringVar(value="⚙️ Initializing...")
        status_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.init_status,
            font=("Arial", 12),
            text_color="#2E7D32"
        )
        status_label.pack(pady=10)
        
        # ===== MAIN CONTENT =====
        content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Chat display area
        chat_label = ctk.CTkLabel(
            content_frame,
            text="💬 Conversation",
            font=("Arial", 16, "bold"),
            text_color="#341B5E"
        )
        chat_label.pack(anchor="w", pady=(0, 5))
        
        # Scrollable chat area
        chat_frame = ctk.CTkFrame(content_frame, fg_color="white", border_width=2, border_color="#81C784")
        chat_frame.pack(fill="both", expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="white",
            fg="#212121",
            relief="flat",
            padx=15,
            pady=15,
            state="disabled"
        )
        self.chat_display.pack(fill="both", expand=True, padx=3, pady=3)
        
        # Configure text tags for styling
        self.chat_display.tag_config("user", foreground="#1565C0", font=("Arial", 11, "bold"))
        self.chat_display.tag_config("buddy", foreground="#2E7D32", font=("Arial", 11, "bold"))
        self.chat_display.tag_config("timestamp", foreground="#757575", font=("Arial", 9))
        self.chat_display.tag_config("error", foreground="#C62828", font=("Arial", 11))
        self.chat_display.tag_config("warning", foreground="#F57C00", font=("Arial", 11))
        
        # Welcome message
        self.add_message("system", "Welcome to PIXEL BUDDY! 🎉\nI'm your soccer rules expert. Ask me anything about soccer!\n(Say 'help' for commands, 'exit' to close, 'skip' to skip)\n")
        
        # ===== INPUT AREA =====
        input_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Text input field
        self.text_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your question here or use voice...",
            height=45,
            font=("Arial", 13),
            border_color="#818DC7",
            border_width=2
        )
        self.text_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.text_input.bind("<Return>", lambda e: self.send_text_message())
        
        # Send button
        self.send_btn = ctk.CTkButton(
            input_frame,
            text="📤 Send",
            command=self.send_text_message,
            width=100,
            height=45,
            font=("Arial", 13, "bold"),
            fg_color="#3E2E7D",
            hover_color="#1E1B5E"
        )
        self.send_btn.pack(side="left", padx=(0, 10))
        
        # Voice button
        self.voice_btn = ctk.CTkButton(
            input_frame,
            text="🎤 Voice",
            command=self.toggle_voice,
            width=100,
            height=45,
            font=("Arial", 13, "bold"),
            fg_color="#1565C0",
            hover_color="#0D47A1"
        )
        self.voice_btn.pack(side="left", padx=(0, 10))
        
        # NEW: Skip button
        self.skip_btn = ctk.CTkButton(
            input_frame,
            text="⏭️ Skip",
            command=self.skip_response,
            width=100,
            height=45,
            font=("Arial", 13, "bold"),
            fg_color="#0A7457",
            hover_color="#049D9B",
            state="disabled"
        )
        self.skip_btn.pack(side="left")
        
        self.exit_btn = ctk.CTkButton(
            input_frame,
            text="🚪 Exit",
            command=self.goodbye_and_close,
            width=100,
            height=45,
            font=("Arial", 13, "bold"),
            fg_color="#C62828",   # Red color for exit
            hover_color="#B71C1C"
        )
        self.exit_btn.pack(side="left", padx=(10, 0)) # Add some space on the left
        # ===== QUICK QUESTIONS =====
        quick_frame = ctk.CTkFrame(self.root, fg_color="#E8F5E9")
        quick_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        quick_label = ctk.CTkLabel(
            quick_frame,
            text="⚡ Quick Questions:",
            font=("Arial", 12, "bold"),
            text_color="#2E607D"
        )
        quick_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        quick_buttons_frame = ctk.CTkFrame(quick_frame, fg_color="transparent")
        quick_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        quick_questions = [
            "What is offside?",
            "How long is a match?",
            "What is a penalty?",
            "Who is Messi?",
            "Tell me about VAR",
            "❓ Help"
        ]
        
        for i, question in enumerate(quick_questions):
            btn = ctk.CTkButton(
                quick_buttons_frame,
                text=question,
                command=lambda q=question: self.quick_question(q),
                width=160,
                height=30,
                font=("Arial", 10),
                fg_color="#6966BB" if question != "❓ Help" else "#2196F3",
                hover_color="#4345A0" if question != "❓ Help" else "#1976D2"
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="ew")
        
        quick_buttons_frame.grid_columnconfigure(0, weight=1)
        quick_buttons_frame.grid_columnconfigure(1, weight=1)
        quick_buttons_frame.grid_columnconfigure(2, weight=1)
    
    def initialize_components(self):
        """Initialize AI components in background"""
        try:
            # Initialize STT
            self.init_status.set("⚙️ Loading Speech Recognition...")
            self.stt = ImprovedSpeechToText(model_name=self.config['stt']['model'])
            
            # Initialize NLP
            self.init_status.set("⚙️ Loading AI Brain...")
            self.nlp = NLPProcessor(
                mode=self.config['nlp']['mode'],
                domain=self.config['system']['domain'],
                use_rag=self.config['nlp']['use_rag'],
                model=self.config['nlp']['model']
            )
            
            # Initialize TTS
            self.init_status.set("⚙️ Loading Voice Output...")
            self.tts = TextToSpeech(
                method=self.config['tts']['method'],
                rate=self.config['tts']['rate'],
                volume=self.config['tts']['volume']
            )
            
            self.init_status.set("✅ Ready! Ask me about soccer!")
            self.add_message("system", "✅ All systems ready! How can I help you today?\n")
            
        except Exception as e:
            self.init_status.set(f"❌ Initialization Error")
            self.add_message("error", f"Error initializing: {str(e)}\n")
            messagebox.showerror("Initialization Error", f"Failed to initialize:\n{str(e)}\n\nPlease check:\n1. Ollama is running\n2. Dataset files exist\n3. All packages installed")
    
    def add_message(self, sender, text):
        """Add message to chat display"""
        self.chat_display.config(state="normal")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if sender == "user":
            self.chat_display.insert("end", f"[{timestamp}] ", "timestamp")
            self.chat_display.insert("end", "You: ", "user")
            self.chat_display.insert("end", f"{text}\n\n")
            
        elif sender == "buddy":
            self.chat_display.insert("end", f"[{timestamp}] ", "timestamp")
            self.chat_display.insert("end", "⚽ PIXEL BUDDY: ", "buddy")
            self.chat_display.insert("end", f"{text}\n\n")
            
        elif sender == "error":
            self.chat_display.insert("end", f"❌ Error: ", "error")
            self.chat_display.insert("end", f"{text}\n\n")
            
        elif sender == "warning":
            self.chat_display.insert("end", f"⚠️  ", "warning")
            self.chat_display.insert("end", f"{text}\n\n")
            
        else:  # system
            self.chat_display.insert("end", f"{text}")
        
        self.chat_display.config(state="disabled")
        self.chat_display.see("end")
    
    def check_exit_command(self, text):
        """Check if user wants to exit"""
        exit_words = ['exit', 'goodbye', 'bye', 'quit', 'close', 'stop']
        text_lower = text.lower().strip()
        
        return any(word in text_lower for word in exit_words)
    
    def check_skip_command(self, text):
        """Check if user wants to skip"""
        skip_words = ['skip', 'next', 'stop speaking']
        text_lower = text.lower().strip()
        
        return any(word in text_lower for word in skip_words)
    
    def check_help_command(self, text):
        """Check if user wants help/info about PIXEL BUDDY"""
        help_keywords = [
            'help', 'how to use', 'what can you do', 'commands',
            'about you', 'who are you', 'what are you',
            'how do you work', 'tell me about yourself',
            'what is pixel buddy', 'features', 'functions'
        ]
        text_lower = text.lower().strip()
        
        return any(keyword in text_lower for keyword in help_keywords)
    
    def show_help(self):
        """Show help information about PIXEL BUDDY"""
        help_text = """🎯 **ABOUT PIXEL BUDDY**

I'm PIXEL BUDDY, your intelligent soccer rules assistant! I can answer questions about soccer rules, players, teams, and the beautiful game! ⚽

🔧 **HOW TO USE ME:**

**Voice Input:**
• Click the 🎤 Voice button
• Speak your question clearly
• I'll transcribe and answer!

**Text Input:**
• Type your question in the text box
• Press Enter or click 📤 Send
• I'll respond with text AND voice!

**Quick Questions:**
• Click any green button below for instant answers
• Perfect for common questions!

⚡ **SPECIAL COMMANDS:**

• Type **"skip"** - Skip current response/speech
• Say **"exit"** or **"goodbye"** - Close PIXEL BUDDY
• Type **"help"** - Show this message again

🎤 **VOICE FEATURES:**
• I always respond with BOTH text and speech
• You can use voice OR text input
• Speech recognition powered by Whisper AI
• Text-to-speech for natural responses

⚽ **WHAT I CAN ANSWER:**
• Soccer rules (offside, fouls, penalties)
• Match information (duration, positions)
• Player information (famous players, stats)
• Tournament details (World Cup, Champions League)
• VAR and referee decisions
• And much more about soccer!

📝 **TIPS FOR BEST RESULTS:**
• Speak clearly for voice input
• Ask specific questions
• Use the Skip button if I'm too slow
• Try Quick Questions for common topics

💡 **EXAMPLE QUESTIONS:**
• "What is the offside rule?"
• "How long is a soccer match?"
• "Tell me about Lionel Messi"
• "What happens during a penalty kick?"
• "Explain the VAR system"

Need anything else? Just ask! I'm here to help! 🚀⚽"""

        return help_text
    
    def skip_response(self):
        self.skip_current = True

        # Clear pending speech
        while not self.tts_queue.empty():
            try:
                self.tts_queue.get_nowait()
            except:
                break

        self.root.after(0, lambda: self.init_status.set("⏭️ Skipped"))
        self.skip_btn.configure(state="disabled")

    
    def send_text_message(self):
        """Send text message"""
        if not self.nlp:
            self.add_message("warning", "Please wait, system is still loading...\n")
            return
        
        text = self.text_input.get().strip()
        if not text:
            return
        
        # Clear input
        self.text_input.delete(0, "end")
        
        # Check for help command
        if self.check_help_command(text):
            self.add_message("user", text)
            help_text = self.show_help()
            self.add_message("buddy", help_text)
            
            # Speak help summary
            if self.tts:
                summary = "I'm PIXEL BUDDY, your soccer assistant! I can answer questions about soccer using voice or text. Type 'help' anytime for more information. What would you like to know about soccer?"
                Thread(target=self.speak_async, args=(summary,), daemon=True).start()
            return
        
        # Check for skip command
        if self.check_skip_command(text):
            self.skip_response()
            return
        
        # Check for exit command
        if self.check_exit_command(text):
            self.add_message("user", text)
            self.goodbye_and_close()
            return
        
        # Process message
        self.process_query(text, input_type="text", stt_duration=0)
    
    def quick_question(self, question):
        """Handle quick question button"""
        self.text_input.delete(0, "end")
        self.text_input.insert(0, question)
        self.send_text_message()
    
    def toggle_voice(self):
        """Toggle voice recording"""
        if not self.stt or not self.nlp:
            self.add_message("warning", "Please wait, system is still loading...\n")
            return
        
        if self.is_listening:
            # Stop listening
            self.is_listening = False
            self.voice_btn.configure(text="🎤 Voice", fg_color="#1565C0")
            return
        
        # Start listening
        self.is_listening = True
        self.voice_btn.configure(text="⏹️ Stop", fg_color="#C62828")
        self.add_message("system", "🎧 Listening... Speak now!\n")
        
        # Record in background thread
        Thread(target=self.record_and_process, daemon=True).start()
    
    def record_and_process(self):
        """Record audio and process"""
        try:
            # Record
            start_stt = time.time()
            text = self.stt.listen_and_transcribe(duration=self.config['stt']['duration'])
            stt_duration = time.time() - start_stt

            # Reset button
            self.voice_btn.configure(text="🎤 Voice", fg_color="#1565C0")
            self.is_listening = False
            
            # Check if valid
            if "[" in text or len(text) < 3:
                self.add_message("warning", "Could not understand speech. Please try again or type your question.\n")
                return
            
            # Check for help command
            if self.check_help_command(text):
                self.add_message("user", text)
                help_text = self.show_help()
                self.add_message("buddy", help_text)
                
                # Speak help summary
                if self.tts:
                    summary = "I'm PIXEL BUDDY, your soccer assistant! I can answer questions about soccer using voice or text. Type 'help' anytime for more information. What would you like to know about soccer?"
                    Thread(target=self.speak_async, args=(summary,), daemon=True).start()
                return
            
            # Check for skip command
            if self.check_skip_command(text):
                self.skip_response()
                return
            
            # Check for exit command
            if self.check_exit_command(text):
                self.add_message("user", text)
                self.goodbye_and_close()
                return
            
            # Process
            self.process_query(text, input_type="voice", stt_duration=stt_duration)
            
        except Exception as e:
            self.add_message("error", f"Voice recording error: {str(e)}\n")
            self.voice_btn.configure(text="🎤 Voice", fg_color="#1565C0")
            self.is_listening = False
    
    def process_query(self, text, input_type="text", stt_duration=0):
        """Process user query"""
        if self.is_processing:
            self.add_message("warning", "Please wait for current response...\n")
            return
        
        self.is_processing = True
        self.skip_current = False  # Reset skip flag
        
        # Enable skip button
        self.skip_btn.configure(state="normal")
        
        # Show user message
        self.add_message("user", text)
        
        # Show processing
        self.init_status.set("⚙️ Thinking...")
        
        # Process in background
        Thread(target=self._process_query_thread, args=(text, input_type, stt_duration), daemon=True).start()
        
    def remove_emojis(self, text):
        """Remove all emojis from text for clean voice output"""
        import re
    
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U0001FA00-\U0001FAFF"
            "]+",
            flags=re.UNICODE
        )
    
        clean_text = emoji_pattern.sub('', text)
        clean_text = ' '.join(clean_text.split())
        return clean_text
    
    def speak_async(self, text):
        if not self.tts or self.is_closing:
            return

        self.is_speaking = True
        self.root.after(0, lambda: self.init_status.set("🔊 Speaking..."))
        self.tts_queue.put(text)

    def after_speaking(self):
        self.is_speaking = False
        self.skip_btn.configure(state="disabled")
        if not self.is_closing:
            self.init_status.set("✅ Ready! Ask me about soccer!")

    def _process_query_thread(self, text, input_type, stt_duration):
        """Process query in background thread"""
        nlp_time = 0
        tts_estimated_time = 0  # Initialize variable
        
        try:
            # Check if skipped before processing
            if self.skip_current:
                self.is_processing = False
                self.skip_btn.configure(state="disabled")
                return
            
            print(f"[DEBUG] Processing query: {text}")
            
            # Get response from NLP
            start_nlp = time.time()
            response = self.nlp.process(text)
            nlp_time = time.time() - start_nlp
            
            print(f"[DEBUG] Got response: {response[:100]}...")
            
            # Check if skipped after processing
            if self.skip_current:
                self.is_processing = False
                self.skip_btn.configure(state="disabled")
                return
            
            # Show response immediately
            self.add_message("buddy", response)
            
            # Mark processing as done
            self.is_processing = False
            
            # Update status
            if not self.is_speaking:
                self.init_status.set("✅ Ready! Ask me about soccer!")
            
            print(f"[DEBUG] About to speak response...")
            
            # ALWAYS speak response in separate thread (unless skipped)
            if self.tts and not self.is_closing and not self.skip_current:
                clean_response = self.remove_emojis(response)
                print(f"[DEBUG] Clean response: {clean_response[:100]}...")
                
                # --- NEW: CALCULATE TTS DURATION ---
                # Calculate seconds based on word count and configured rate
                word_count = len(clean_response.split())
                speech_rate = self.config['tts'].get('rate', 150) # Default to 150 wpm if missing
                tts_estimated_time = (word_count / speech_rate) * 60.0
                # -----------------------------------

                # Start speech thread
                speech_thread = Thread(target=self.speak_async, args=(clean_response,), daemon=True)
                speech_thread.start()
                print(f"[DEBUG] Speech thread started")
            else:
                print(f"[DEBUG] Speech skipped")
                self.skip_btn.configure(state="disabled")
            
        except Exception as e:
            print(f"❌ Processing error: {e}")
            import traceback
            traceback.print_exc()
            self.add_message("error", f"Processing error: {str(e)}\n")
            self.init_status.set("❌ Error occurred")
            self.is_processing = False
            self.skip_btn.configure(state="disabled")

        try:
            # Add the estimated TTS time to the total
            total_time = stt_duration + nlp_time + tts_estimated_time
            
            if nlp_time > 0:
                self.logger.log(
                    input_type=input_type,
                    query_length=len(text),
                    stt_time=stt_duration,
                    nlp_time=nlp_time,
                    tts_time=tts_estimated_time,  # <--- NOW SAVES REAL NUMBER
                    total_time=total_time,
                    tts_success=True
                )
                print(f"📊 Metrics logged: NLP {nlp_time:.2f}s, TTS {tts_estimated_time:.2f}s")
        except Exception as e:
            print(f"❌ Logging error: {e}")
    
    def goodbye_and_close(self):
        """Say goodbye and close application"""
        if self.is_closing:
            return
        
        self.is_closing = True
        self.skip_current = True  # Stop any current speech
        
        goodbye_msg = "Goodbye! Thanks for using PIXEL BUDDY. See you next time! ⚽"
        self.add_message("buddy", goodbye_msg)
        
        # Speak goodbye
        if self.tts:
            clean_msg = self.remove_emojis(goodbye_msg)
            try:
                if self.tts.method == "pyttsx3":
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.setProperty('rate', self.config['tts']['rate'])
                    engine.setProperty('volume', self.config['tts']['volume'])
                    engine.say(clean_msg)
                    engine.runAndWait()
                    engine.stop()
                else:
                    self.tts.speak(clean_msg)
            except:
                pass
        
        # Close after 2 seconds
        self.root.after(2000, self.close_application)
    
    def on_closing(self):
        """Handle window close button"""
        self.goodbye_and_close()
    
    def close_application(self):
        """Close the application"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        sys.exit(0)
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║              ⚽ PIXEL BUDDY GUI ⚽                        ║
    ║         Soccer Rules Voice Assistant                     ║
    ║                                                          ║
    ║  Starting beautiful GUI interface...                     ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        app = PixelBuddyGUI()
        app.run()
    except Exception as e:
        print(f"❌ Failed to start GUI: {e}")
        print("\nPlease make sure:")
        print("1. All packages are installed: pip install -r requirements.txt")
        print("2. Ollama is running: ollama serve")
        print("3. Dataset files exist in datasets/ folder")