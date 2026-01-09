"""
Dataset Loader for PIXEL BUDDY
Loads local datasets + Wikipedia articles
"""

import json
import os
from typing import List, Dict

class DatasetLoader:
    def __init__(self):
        self.datasets = []
        
    def load_local_json(self, filepath: str) -> List[Dict]:
        """Load local JSON dataset"""
        if not os.path.exists(filepath):
            print(f"⚠️  File not found: {filepath}")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Loaded {len(data)} documents from {filepath}")
            return data
        except Exception as e:
            print(f"❌ Error loading {filepath}: {e}")
            return []
    
    def load_wikipedia_topics(self, topics: List[str], max_length=3000, lang='en') -> List[Dict]:
        """
        Load Wikipedia articles for soccer topics
        
        Args:
            topics: List of topics to fetch
            max_length: Max characters per article
            lang: Language code
        """
        try:
            import wikipedia
            wikipedia.set_lang(lang)
        except ImportError:
            print("⚠️  Wikipedia package not installed!")
            print("   Install with: pip install wikipedia")
            return []
        
        documents = []
        
        print(f"\n📥 Fetching {len(topics)} Wikipedia articles about soccer...")
        
        for i, topic in enumerate(topics, 1):
            try:
                print(f"   [{i}/{len(topics)}] Fetching: {topic}...", end=" ")
                
                page = wikipedia.page(topic, auto_suggest=False)
                
                # Get content (limit length)
                content = page.content[:max_length]
                
                documents.append({
                    "source": f"Wikipedia - {page.title}",
                    "category": "wikipedia",
                    "content": content,
                    "url": page.url
                })
                
                print("✅")
                
            except wikipedia.exceptions.DisambiguationError as e:
                # Multiple options, use first one
                try:
                    print(f"⚠️  Ambiguous, using: {e.options[0]}")
                    page = wikipedia.page(e.options[0])
                    content = page.content[:max_length]
                    
                    documents.append({
                        "source": f"Wikipedia - {page.title}",
                        "category": "wikipedia",
                        "content": content,
                        "url": page.url
                    })
                except:
                    print(f"❌ Failed")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}")
        
        print(f"\n✅ Successfully loaded {len(documents)} Wikipedia articles\n")
        return documents
    
    def load_all_datasets(self, config: Dict) -> List[Dict]:
        """
        Load all configured datasets
        
        Args:
            config: Configuration dictionary
        """
        all_documents = []
        
        print("="*60)
        print("📚 LOADING DATASETS")
        print("="*60)
        
        # Load local datasets
        if 'local_datasets' in config:
            print("\n1️⃣  Loading local datasets...")
            for dataset_path in config['local_datasets']:
                docs = self.load_local_json(dataset_path)
                all_documents.extend(docs)
        
        # Load Wikipedia topics
        if config.get('enable_wikipedia', False) and 'wikipedia_topics' in config:
            print("\n2️⃣  Loading Wikipedia articles...")
            docs = self.load_wikipedia_topics(
                config['wikipedia_topics'],
                max_length=config.get('max_wikipedia_length', 3000)
            )
            all_documents.extend(docs)
        
        print("="*60)
        print(f"✅ TOTAL DOCUMENTS LOADED: {len(all_documents)}")
        print("="*60)
        print()
        
        return all_documents


if __name__ == "__main__":
    # Test the dataset loader
    import yaml
    
    print("Testing Dataset Loader...")
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    loader = DatasetLoader()
    docs = loader.load_all_datasets(config.get('datasets', {}))
    
    # Show breakdown
    sources = {}
    for doc in docs:
        source = doc.get('source', 'Unknown')
        source_type = 'Wikipedia' if 'Wikipedia' in source else 'Soccer Rules'
        sources[source_type] = sources.get(source_type, 0) + 1
    
    print("\n📊 Documents by source:")
    for source, count in sources.items():
        print(f"   {source}: {count} documents")
    
    # Show sample
    if docs:
        print(f"\n📄 Sample document:")
        print(f"   Source: {docs[0]['source']}")
        print(f"   Category: {docs[0]['category']}")
        print(f"   Content: {docs[0]['content'][:200]}...")