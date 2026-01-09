"""Test Ollama local LLM"""

try:
    import ollama
    
    print("="*60)
    print("TESTING OLLAMA LOCAL LLM")
    print("="*60)
    
    # Check if Ollama is running
    print("\n1. Checking Ollama service...")
    try:
        models = ollama.list()
        print("✅ Ollama is running!")
        print(f"   Available models: {[m['name'] for m in models['models']]}")
    except Exception as e:
        print(f"❌ Ollama not running: {e}")
        print("   Start with: ollama serve")
        exit(1)
    
    # Test chat
    print("\n2. Testing chat completion...")
    response = ollama.chat(
        model='llama2',
        messages=[{
            'role': 'user',
            'content': 'Say hello in one sentence.'
        }]
    )
    
    print(f"✅ Response: {response['message']['content']}")
    
    print("\n" + "="*60)
    print("Ollama test complete!")
    print("="*60)
    
except ImportError:
    print("❌ Ollama not installed!")
    print("   Install with: pip install ollama")