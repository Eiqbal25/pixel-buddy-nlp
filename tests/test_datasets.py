"""Test the expanded dataset system"""
import os
import sys
sys.path.append('..')
import yaml

# ------------------------------------------------------------------
# PATH SETUP (Fixes ModuleNotFoundError & FileNotFoundError)
# ------------------------------------------------------------------
# 1. Get the path to the current folder ('tests')
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Get the main project folder (Go up one level)
project_root = os.path.dirname(current_dir)

# 3. Add project root to Python's search path (so it finds 'dataset_loader.py')
sys.path.append(project_root)

# 4. Also add the 'script' folder if your file is hiding in there
script_folder = os.path.join(project_root, 'script')
sys.path.append(script_folder)
# ------------------------------------------------------------------

# NOW import your custom modules
from dataset_loader import DatasetLoader  # This should work now

# Load Config safely
config_path = os.path.join(project_root, 'config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)
    print("✅ Config loaded successfully")



print("="*60)
print("TESTING EXPANDED DATASET SYSTEM")
print("="*60)

# Load configuration
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

dataset_config = config.get('datasets', {})

# Initialize loader
loader = DatasetLoader()

# Test loading all datasets
print("\n📚 Loading all configured datasets...")
docs = loader.load_all_datasets(dataset_config)

print(f"\n✅ Total documents loaded: {len(docs)}")

# Show breakdown
sources = {}
for doc in docs:
    source = doc.get('source', 'Unknown')
    source_type = source.split(' - ')[0] if ' - ' in source else source
    sources[source_type] = sources.get(source_type, 0) + 1

print("\n📊 Documents by source:")
for source, count in sources.items():
    print(f"   {source}: {count} documents")

# Show sample
if docs:
    print(f"\n📄 Sample document:")
    print(f"   Source: {docs[0]['source']}")
    print(f"   Category: {docs[0]['category']}")
    print(f"   Content (first 200 chars): {docs[0]['content'][:200]}...")

print("\n" + "="*60)
print("Dataset test complete!")
print("="*60)