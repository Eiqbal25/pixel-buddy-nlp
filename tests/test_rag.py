"""Test RAG system"""
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

import sys
sys.path.append('..')

from nlp_processor import NLPProcessor

print("="*60)
print("TESTING RAG SYSTEM")
print("="*60)

print("\nInitializing NLP Processor with RAG...")
nlp = NLPProcessor(mode="local", use_rag=True)

test_queries = [
    "What is offside in soccer?",          # From rules
    "Who is Lionel Messi?",                # From Wikipedia
    "How long is a soccer match?",         # From rules
    "What is the FIFA World Cup?",         # From Wikipedia
    "What is a penalty kick?"              # From rules
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*60}")
    print(f"Test {i}/{len(test_queries)}: {query}")
    print(f"{'='*60}")
    
    # Get relevant context
    context = nlp.get_relevant_context(query, k=2)
    print(f"\n📚 Retrieved Context (first 200 chars):")
    print(context[:200] + "...")
    
    # Get full response
    response = nlp.process(query)
    print(f"\n🤖 Response:")
    print(response)

print("\n" + "="*60)
print("RAG test complete!")
print("="*60)