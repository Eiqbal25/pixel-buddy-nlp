"""Test Speech-to-Text module"""

import sys
import os
sys.path.append('..')
# ------------------------------------------------------------------
# PATH FIX: Allow importing from the main folder
# ------------------------------------------------------------------
# 1. Get the path to the current folder (C:\voice assistant NLP\tests)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Go up one level to the main project folder (C:\voice assistant NLP)
parent_dir = os.path.dirname(current_dir)

# 3. Add the main folder to Python's visible paths
sys.path.append(parent_dir)
# ------------------------------------------------------------------

from stt_improved import ImprovedSpeechToText

print("="*60)
print("TESTING SPEECH-TO-TEXT MODULE")
print("="*60)

stt = ImprovedSpeechToText(model_name="base")

print("\nTest: Record and transcribe")
print("Speak something when prompted...")

text = stt.listen_and_transcribe(duration=5)

print(f"\n✅ Transcribed Text: {text}")
print("\nTest complete!")