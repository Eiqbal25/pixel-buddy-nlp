"""Test the topic filter"""
import sys
import os
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

from nlp_processor import NLPProcessor

print("Testing Topic Filter...")
print("="*60)

nlp = NLPProcessor(mode="local", use_rag=False)  # No RAG needed for this test

# Test cases
test_cases = [
    # Soccer questions
    ("What is offside?", True),
    ("Who is Messi?", True),
    ("Tell me about FIFA", True),
    ("How long is a soccer match?", True),
    
    # Non-soccer questions
    ("What is Python?", False),
    ("How to cook pasta?", False),
    ("Tell me about basketball", False),
    ("What is the weather?", False),
]

correct = 0
for question, should_be_soccer in test_cases:
    is_soccer = nlp.is_soccer_related(question)
    status = "✅" if is_soccer == should_be_soccer else "❌"
    
    print(f"{status} '{question}'")
    print(f"   Expected: {'Soccer' if should_be_soccer else 'Not Soccer'}")
    print(f"   Got: {'Soccer' if is_soccer else 'Not Soccer'}")
    print()
    
    if is_soccer == should_be_soccer:
        correct += 1

print("="*60)
print(f"Accuracy: {correct}/{len(test_cases)} ({100*correct//len(test_cases)}%)")