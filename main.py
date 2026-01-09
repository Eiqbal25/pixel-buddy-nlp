"""
PIXEL BUDDY - Console Version
Voice Assistant without GUI - runs in terminal/VS Code
"""

import yaml
import sys
from threading import Thread, Event
import time

# Import our modules
from stt_improved import ImprovedSpeechToText
from nlp_processor import NLPProcessor
from tts import TextToSpeech
from metrics_logger import MetricsLogger  # <--- NEW IMPORT

class PixelBuddyConsole:
    def __init__(self):
        """Initialize PIXEL BUDDY Console"""
        print("⚙️  Initializing PIXEL BUDDY...")
        
        # Load configuration
        with open('config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Flags
        self.skip_current = False
        self.is_speaking = False
        self.is_processing = False
        self.running = True
        
        # Initialize Logger
        self.logger = MetricsLogger() # <--- NEW LOGGER
        
        # Initialize components
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize AI components"""
        try:
            # Initialize STT
            print("📥 Loading Speech Recognition...")
            self.stt = ImprovedSpeechToText(model_name=self.config['stt']['model'])
            
            # Initialize NLP
            print("🧠 Loading AI Brain...")
            self.nlp = NLPProcessor(
                mode=self.config['nlp']['mode'],
                domain=self.config['system']['domain'],
                use_rag=self.config['nlp']['use_rag'],
                model=self.config['nlp']['model']
            )
            
            # Initialize TTS
            print("🔊 Loading Voice Output...")
            self.tts = TextToSpeech(
                method=self.config['tts']['method'],
                rate=self.config['tts']['rate'],
                volume=self.config['tts']['volume']
            )
            
            print("✅ All systems ready!\n")
            
        except Exception as e:
            print(f"❌ Initialization Error: {e}")
            sys.exit(1)
    
    def remove_emojis(self, text):
        """Remove emojis for clean voice output"""
        import re
        
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001F900-\U0001F9FF"
            "\U0001FA00-\U0001FAFF"
            "]+",
            flags=re.UNICODE
        )
        
        clean_text = emoji_pattern.sub('', text)
        return ' '.join(clean_text.split())
    
    def check_exit_command(self, text):
        """Check if user wants to exit"""
        exit_words = ['exit', 'goodbye', 'bye', 'quit', 'close', 'stop']
        return any(word in text.lower().strip() for word in exit_words)
    
    def check_skip_command(self, text):
        """Check if user wants to skip"""
        skip_words = ['skip', 'next', 'stop speaking']
        return any(word in text.lower().strip() for word in skip_words)
    
    def check_help_command(self, text):
        """Check if user wants help/info about PIXEL BUDDY"""
        help_keywords = [
            'help', 'how to use', 'what can you do', 'commands',
            'about you', 'who are you', 'what are you',
            'how do you work', 'tell me about yourself',
            'what is pixel buddy', 'features', 'functions'
        ]
        return any(keyword in text.lower().strip() for keyword in help_keywords)
    
    def show_help(self):
        """Show help information about PIXEL BUDDY"""
        help_text = """
╔══════════════════════════════════════════════════════════╗
║          🎯 ABOUT PIXEL BUDDY (CONSOLE MODE)            ║
╚══════════════════════════════════════════════════════════╝
I'm PIXEL BUDDY, your intelligent soccer rules assistant! ⚽
"""
        return help_text
    
    def speak(self, text):
        """Speak text with skip support"""
        if self.skip_current:
            return
        
        try:
            self.is_speaking = True
            clean_text = self.remove_emojis(text)
            
            if self.tts.method == "pyttsx3":
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', self.config['tts']['rate'])
                engine.setProperty('volume', self.config['tts']['volume'])
                
                # Speak in chunks for skip support
                words = clean_text.split()
                chunk_size = 20
                
                for i in range(0, len(words), chunk_size):
                    if self.skip_current:
                        engine.stop()
                        break
                    chunk = ' '.join(words[i:i+chunk_size])
                    engine.say(chunk)
                    engine.runAndWait()
                
                engine.stop()
            else:
                self.tts.speak(clean_text)
                
        except Exception as e:
            print(f"TTS Error: {e}")
        finally:
            self.is_speaking = False
    
    def process_voice_query(self):
        """Process voice input"""
        try:
            print("\n🎤 Listening... (Speak now)")
            
            # --- START STT TIMER ---
            start_stt = time.time()
            text = self.stt.listen_and_transcribe(duration=self.config['stt']['duration'])
            stt_duration = time.time() - start_stt
            # --- END STT TIMER ---
            
            # Check if valid
            if "[" in text or len(text) < 3:
                print("⚠️  Could not understand. Please try again.\n")
                return
            
            print(f"📝 You said: {text} (STT took {stt_duration:.2f}s)")
            
            # Check for help command
            if self.check_help_command(text):
                help_text = self.show_help()
                print(help_text)
                summary = "I'm PIXEL BUDDY, your soccer assistant! Type 'help' anytime for more information."
                self.speak(summary)
                return
            
            # Check commands
            if self.check_skip_command(text):
                self.skip_current = True
                print("⏭️  Skipping...\n")
                return
            
            if self.check_exit_command(text):
                self.goodbye()
                return
            
            # Process query with measured STT time
            self.process_query(text, input_type="voice", stt_time=stt_duration)
            
        except Exception as e:
            print(f"❌ Voice error: {e}\n")
    
    def process_text_query(self, text):
        """Process text input"""
        if not text.strip():
            return
        
        print(f"📝 You: {text}")
        
        # Check for help command
        if self.check_help_command(text):
            help_text = self.show_help()
            print(help_text)
            summary = "I'm PIXEL BUDDY, your soccer assistant! Type 'help' anytime for more information."
            self.speak(summary)
            return
        
        # Check commands
        if self.check_skip_command(text):
            self.skip_current = True
            print("⏭️  Skipping...\n")
            return
        
        if self.check_exit_command(text):
            self.goodbye()
            return
        
        # Process query (STT time is 0 for text input)
        self.process_query(text, input_type="text", stt_time=0)
    
    def process_query(self, text, input_type="text", stt_time=0):
        """Process query and generate response"""
        if self.is_processing:
            print("⚠️  Please wait for current response...\n")
            return
        
        self.is_processing = True
        self.skip_current = False
        
        nlp_time = 0
        tts_time = 0
        tts_success = False
        
        try:
            print("⚙️  Thinking...")
            
            # --- START NLP TIMER ---
            start_nlp = time.time()
            response = self.nlp.process(text)
            nlp_time = time.time() - start_nlp
            # --- END NLP TIMER ---
            
            if self.skip_current:
                print("⏭️  Response skipped.\n")
                self.is_processing = False
                return
            
            # Display response
            print(f"\n⚽ PIXEL BUDDY: {response}")
            print(f"   (NLP Time: {nlp_time:.2f}s)\n")
            
            # Speak response
            if not self.skip_current:
                print("🔊 Speaking...")
                
                # --- START TTS TIMER ---
                start_tts = time.time()
                self.speak(response)
                tts_time = time.time() - start_tts
                tts_success = True
                # --- END TTS TIMER ---
            
            if self.skip_current:
                print("⏭️  Speech skipped.\n")
                tts_success = False # technically skipped
            
        except Exception as e:
            print(f"❌ Error: {e}\n")
            tts_success = False
        finally:
            self.is_processing = False
            
            # --- LOG METRICS ---
            total_time = stt_time + nlp_time + tts_time
            
            # Only log valid interactions (where NLP actually ran)
            if nlp_time > 0:
                self.logger.log(
                    input_type=input_type,
                    query_length=len(text),
                    stt_time=stt_time,
                    nlp_time=nlp_time,
                    tts_time=tts_time,
                    total_time=total_time,
                    tts_success=tts_success
                )
                print(f"📊 Metrics logged: Total time {total_time:.2f}s")

    def goodbye(self):
        """Say goodbye and exit"""
        self.running = False
        self.skip_current = True
        
        goodbye_msg = "Goodbye! Thanks for using PIXEL BUDDY. See you next time!"
        print(f"\n⚽ PIXEL BUDDY: {goodbye_msg}\n")
        
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', self.config['tts']['rate'])
            engine.setProperty('volume', self.config['tts']['volume'])
            engine.say(goodbye_msg)
            engine.runAndWait()
            engine.stop()
        except:
            pass
        
        print("👋 Closing PIXEL BUDDY...")
        sys.exit(0)
    
    def run(self):
        """Run the console interface"""
        print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              ⚽ PIXEL BUDDY CONSOLE ⚽                    ║
║         Soccer Rules Voice Assistant                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
        """)
        
        while self.running:
            try:
                user_input = input("\n💬 You (v=voice, s=skip, help=info): ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['voice', 'v']:
                    self.process_voice_query()
                elif user_input.lower() in ['skip', 's']:
                    if self.is_processing or self.is_speaking:
                        self.skip_current = True
                        print("⏭️  Skipping current response/speech...\n")
                    else:
                        print("⚠️  Nothing to skip.\n")
                elif user_input.lower() in ['help', 'h', '?']:
                    help_text = self.show_help()
                    print(help_text)
                else:
                    self.process_text_query(user_input)
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user.")
                self.goodbye()
            except EOFError:
                self.goodbye()
            except Exception as e:
                print(f"❌ Error: {e}")
                continue


if __name__ == "__main__":
    print("Starting console interface...")
    try:
        app = PixelBuddyConsole()
        app.run()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        sys.exit(1)