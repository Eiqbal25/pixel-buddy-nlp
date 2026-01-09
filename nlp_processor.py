"""
NLP Processing Module - PIXEL BUDDY with Topic Filter
Only answers soccer-related questions!
"""

import os
from dotenv import load_dotenv
import json
import yaml

# For local LLM
try:
    import ollama
except:
    pass

# For API mode
try:
    from anthropic import Anthropic
except:
    pass

# For RAG
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain.schema import Document
except:
    pass

# Import dataset loader
from dataset_loader import DatasetLoader

class NLPProcessor:
    def __init__(self, mode="local", domain="soccer", use_rag=True, model="llama2"):
        """Initialize PIXEL BUDDY with topic filtering"""
        load_dotenv()
        
        self.mode = mode
        self.domain = domain
        self.use_rag = use_rag
        self.model = model
        
        print(f"⚽ Initializing PIXEL BUDDY with topic filter...")
        print(f"   Mode: {mode}")
        print(f"   Domain: {domain}")
        print(f"   RAG: {use_rag}")
        print(f"   Model: {model}")
        
        # Initialize LLM
        if mode == "api":
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Initialize RAG
        if use_rag:
            self.setup_rag()
        
        self.system_prompt = self.get_system_prompt()
        print("✅ PIXEL BUDDY ready with topic filter!")
    
    def setup_rag(self):
        """Setup RAG with soccer rules + Wikipedia"""
        print("\n⚽ Setting up knowledge base...")
        
        try:
            # Load configuration
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            dataset_config = config.get('datasets', {})
            
            # Load all datasets (local + Wikipedia)
            loader = DatasetLoader()
            knowledge_docs = loader.load_all_datasets(dataset_config)
            
            if not knowledge_docs:
                print("⚠️  No documents loaded!")
                self.use_rag = False
                return
            
            # Initialize embeddings
            print("🔄 Creating embeddings...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # Create text chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            
            docs = []
            for doc in knowledge_docs:
                chunks = text_splitter.split_text(doc['content'])
                for chunk in chunks:
                    docs.append(Document(
                        page_content=chunk,
                        metadata={
                            "source": doc.get('source', 'Unknown'),
                            "category": doc.get('category', 'general')
                        }
                    ))
            
            # Create vector store
            print("🔄 Building vector database...")
            self.vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            
            print(f"\n✅ RAG READY!")
            print(f"   Total chunks: {len(docs)}")
            print(f"   Sources: Soccer Rules + Wikipedia\n")
            
        except Exception as e:
            print(f"⚠️  RAG setup failed: {e}")
            import traceback
            traceback.print_exc()
            self.use_rag = False
    
    def is_soccer_related(self, query: str) -> bool:
        """
        Check if the query is about soccer/football
        Returns True if soccer-related, False otherwise
        """
        query_lower = query.lower()
        
        # Soccer-related keywords
        soccer_keywords = [
            # Sport names
            'soccer', 'football', 'futbol', 'fifa', 'uefa',
            
            # Rules and gameplay
            'offside', 'penalty', 'foul', 'goal', 'kick', 'referee',
            'card', 'yellow', 'red', 'free kick', 'corner', 'throw-in',
            'goalkeeper', 'goalie', 'var', 'substitution',
            
            # Field and equipment
            'field', 'pitch', 'ball', 'net', 'post', 'crossbar',
            
            # Match terms
            'match', 'game', 'half time', 'extra time', 'stoppage',
            'tournament', 'league', 'cup', 'championship',
            
            # Positions
            'striker', 'midfielder', 'defender', 'forward', 'winger',
            
            # Famous tournaments
            'world cup', 'champions league', 'premier league', 'la liga',
            'serie a', 'bundesliga', 'euro', 'copa america',
            
            # Famous players (from Wikipedia topics)
            'messi', 'ronaldo', 'pele', 'maradona', 'neymar',
            'benzema', 'mbappe', 'haaland',
            
            # Tactics
            'formation', 'tactic', 'strategy', 'defense', 'attack',
            'counter attack', 'possession',
            
            # Organizations
            'club', 'team', 'national team',
            
            # General
            'play', 'player', 'coach', 'manager', 'fan'
        ]
        
        # Check if any soccer keyword is in the query
        for keyword in soccer_keywords:
            if keyword in query_lower:
                return True
        
        # Additional check: if query mentions scoring, playing, winning in context
        context_words = ['score', 'win', 'lose', 'draw', 'play']
        for word in context_words:
            if word in query_lower:
                # Only consider soccer-related if other sports aren't mentioned
                other_sports = ['basketball', 'tennis', 'cricket', 'rugby', 
                               'baseball', 'hockey', 'volleyball', 'badminton']
                if not any(sport in query_lower for sport in other_sports):
                    return True
        
        return False
    
    def get_relevant_context(self, query, k=3):
        """Retrieve relevant context using RAG"""
        if not self.use_rag:
            return ""
        
        try:
            docs = self.vectorstore.similarity_search(query, k=k)
            context = "\n\n".join([
                f"[{doc.metadata['source']}]\n{doc.page_content}"
                for doc in docs
            ])
            return context
        except:
            return ""
    
    def get_system_prompt(self):
        """Soccer assistant system prompt"""
        return """You are PIXEL BUDDY, an intelligent soccer assistant. 

Your knowledge includes:
- FIFA official soccer rules and regulations
- Soccer history, teams, and players
- Famous matches and tournaments
- Soccer tactics and strategies

Guidelines:
- Provide accurate information about soccer
- Use context from FIFA rules or Wikipedia when available
- Explain clearly in 2-3 sentences
- Be friendly and enthusiastic about soccer!
- If asked about rules, prioritize FIFA official rules
- If asked about history/players, use Wikipedia knowledge"""
    
    def process_with_local(self, user_input, context=""):
        """Process using local Ollama"""
        try:
            prompt = self.system_prompt + "\n\n"
            
            if context:
                prompt += f"Relevant Information:\n{context}\n\n"
            
            prompt += f"Question: {user_input}\n\nAnswer (2-3 sentences):"
            
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response['message']['content']
            
        except Exception as e:
            return f"Sorry, error occurred. Is Ollama running? Error: {str(e)}"
    
    def process_with_api(self, user_input, context=""):
        """Process using Claude API"""
        try:
            prompt = self.system_prompt + "\n\n"
            
            if context:
                prompt += f"Relevant Information:\n{context}\n\n"
            
            prompt += f"Question: {user_input}\n\nProvide a helpful answer:"
            
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
            
        except Exception as e:
            return f"Sorry, error: {str(e)}"
    
    def process(self, user_input):
        """
        Main processing method with topic filtering
        """
        try:
            # ===== NEW: CHECK IF QUESTION IS ABOUT SOCCER =====
            if not self.is_soccer_related(user_input):
                print("⚠️  Non-soccer question detected!")
                return "Sorry, I'm not an expert in other fields, but I am an expert in soccer rules and soccer knowledge! Please ask me questions about soccer, football rules, players, teams, or tournaments."
            
            # Question is about soccer, proceed normally
            print("✅ Soccer-related question detected!")
            
            # Get relevant context
            context = ""
            if self.use_rag:
                print("🔍 Searching knowledge base...")
                context = self.get_relevant_context(user_input)
            
            # Process
            if self.mode == "api":
                response = self.process_with_api(user_input, context)
            else:
                response = self.process_with_local(user_input, context)
            
            return response.strip()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return "I apologize, I encountered an error. Please try again."


if __name__ == "__main__":
    # Test PIXEL BUDDY with topic filter
    print("Testing PIXEL BUDDY with topic filter...")
    
    nlp = NLPProcessor(mode="local", use_rag=True)
    
    test_queries = [
        # Soccer questions (should answer)
        "What is offside in soccer?",
        "Who is Lionel Messi?",
        "How long is a soccer match?",
        
        # Non-soccer questions (should reject)
        "What is the capital of France?",
        "How do I cook pasta?",
        "What is Python programming?",
        "Tell me about basketball",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Q: {query}")
        print(f"{'='*60}")
        response = nlp.process(query)
        print(f"A: {response}")