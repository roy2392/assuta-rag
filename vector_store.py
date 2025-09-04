import os
import json
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from typing import List, Dict
import time

class VectorStore:
    def __init__(self, collection_name="assuta_oncology"):
        # Initialize OpenAI client
        from dotenv import load_dotenv
        load_dotenv()
        
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = collection_name
        
        # Create or get collection
        try:
            self.collection = self.chroma_client.get_collection(name=collection_name)
            print(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"description": "Assuta oncology Hebrew content embeddings"}
            )
            print(f"Created new collection: {collection_name}")
    
    def get_embeddings(self, texts: List[str], batch_size=100):
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model="text-embedding-ada-002"
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                print(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error generating embeddings for batch {i//batch_size + 1}: {str(e)}")
                # Add empty embeddings for failed batches to maintain alignment
                embeddings.extend([[0.0] * 1536] * len(batch))
        
        return embeddings
    
    def add_documents(self, chunks: List[Dict]):
        if not chunks:
            print("No chunks to add")
            return
        
        print(f"Adding {len(chunks)} documents to vector store...")
        
        # Prepare data for embedding
        texts = [chunk['content'] for chunk in chunks]
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        # Create metadata
        metadatas = []
        for i, chunk in enumerate(chunks):
            metadata = {
                'title': chunk.get('title', ''),
                'url': chunk.get('url', ''),
                'chunk_id': str(chunk.get('chunk_id', i)),
                'tokens': chunk.get('tokens', 0)
            }
            metadatas.append(metadata)
        
        # Generate embeddings
        embeddings = self.get_embeddings(texts)
        
        # Add to ChromaDB in batches
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch_end = min(i + batch_size, len(chunks))
            
            try:
                self.collection.add(
                    ids=ids[i:batch_end],
                    embeddings=embeddings[i:batch_end],
                    documents=texts[i:batch_end],
                    metadatas=metadatas[i:batch_end]
                )
                print(f"Added batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
            except Exception as e:
                print(f"Error adding batch {i//batch_size + 1}: {str(e)}")
        
        print(f"Successfully added {len(chunks)} documents to vector store")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        try:
            # Generate embedding for query
            query_embedding = self.get_embeddings([query])[0]
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                result = {
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'relevance_score': 1 - results['distances'][0][i]  # Convert distance to relevance
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching: {str(e)}")
            return []
    
    def get_collection_stats(self):
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection_name
            }
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return {'total_documents': 0, 'collection_name': self.collection_name}
    
    def clear_collection(self):
        try:
            # Delete the collection
            self.chroma_client.delete_collection(name=self.collection_name)
            
            # Recreate it
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Assuta oncology Hebrew content embeddings"}
            )
            print(f"Cleared and recreated collection: {self.collection_name}")
        except Exception as e:
            print(f"Error clearing collection: {str(e)}")

def build_vector_store():
    # Load processed chunks - try the better data first
    chunks_file = "scraped_data/scraped_oncology_data.json"
    if not os.path.exists(chunks_file):
        chunks_file = "scraped_data/processed_chunks.json"
        if not os.path.exists(chunks_file):
            print(f"No processed chunks file found. Run document_processor.py first.")
            return None
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert data to chunks format if needed
    if isinstance(data, list) and len(data) > 0:
        if 'content' in data[0] and 'chunk_id' not in data[0]:
            # This is the scraped_oncology_data format, convert it
            chunks = []
            for i, item in enumerate(data):
                content = item.get('hebrew_content') or item.get('content', '')
                chunks.append({
                    'content': f"כותרת: {item['title']}\nמקור: {item['url']}\n\n{content}",
                    'title': item['title'],
                    'url': item['url'],
                    'chunk_id': i,
                    'tokens': len(content.split()) * 1.3
                })
        else:
            # This is already in chunks format
            chunks = data
    else:
        chunks = data
    
    print(f"Loaded {len(chunks)} processed chunks")
    
    # Initialize vector store
    vector_store = VectorStore()
    
    # Check if collection already has data
    stats = vector_store.get_collection_stats()
    if stats['total_documents'] > 0:
        response = input(f"Collection already contains {stats['total_documents']} documents. Clear and rebuild? (y/n): ")
        if response.lower() == 'y':
            vector_store.clear_collection()
        else:
            print("Keeping existing collection")
            return vector_store
    
    # Add documents to vector store
    vector_store.add_documents(chunks)
    
    # Print final stats
    final_stats = vector_store.get_collection_stats()
    print(f"\nVector store built successfully:")
    print(f"Total documents: {final_stats['total_documents']}")
    
    return vector_store

def test_search():
    vector_store = VectorStore()
    
    # Test searches in Hebrew
    test_queries = [
        "טיפול בסרטן השד",
        "כימותרפיה",
        "אונקולוגיה",
        "קרינה",
        "ביופסיה"
    ]
    
    for query in test_queries:
        print(f"\nSearching for: {query}")
        results = vector_store.search(query, n_results=3)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. Score: {result['relevance_score']:.3f}")
            print(f"   Title: {result['metadata']['title']}")
            print(f"   Content preview: {result['content'][:150]}...")
            print()

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_search()
    else:
        build_vector_store()

if __name__ == "__main__":
    main()