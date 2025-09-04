import json
import os
import tiktoken
from typing import List, Dict
import re

class DocumentProcessor:
    def __init__(self, model_name="gpt-3.5-turbo"):
        self.model_name = model_name
        self.encoding = tiktoken.encoding_for_model(model_name)
        self.max_chunk_size = 500  # tokens
        self.chunk_overlap = 50    # tokens
        
    def load_scraped_data(self, filepath="scraped_data/scraped_oncology_data.json"):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def clean_hebrew_text(self, text):
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common web artifacts
        text = re.sub(r'Skip to main content', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Cookie|Cookies', '', text, flags=re.IGNORECASE)
        text = re.sub(r'JavaScript|javascript', '', text, flags=re.IGNORECASE)
        
        # Remove English navigation elements
        text = re.sub(r'\b(Home|Contact|About|Menu|Search|Login|Register)\b', '', text)
        
        # Clean up common Hebrew web artifacts
        text = re.sub(r'לחץ כאן|קישור|תפריט|חפש|התחבר|הירשם', '', text)
        
        return text.strip()
    
    def count_tokens(self, text):
        return len(self.encoding.encode(text))
    
    def split_into_chunks(self, text, title="", url=""):
        chunks = []
        
        # Clean the text
        text = self.clean_hebrew_text(text)
        
        if not text or len(text.strip()) < 50:
            return chunks
        
        # Split by sentences for Hebrew text
        sentences = re.split(r'[.!?।׃]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        current_chunk = ""
        current_tokens = 0
        
        # Add title and URL context to first chunk
        context = ""
        if title:
            context += f"כותרת: {title}\n"
        if url:
            context += f"מקור: {url}\n"
        context += "\n"
        
        context_tokens = self.count_tokens(context)
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            # If adding this sentence would exceed max chunk size
            if current_tokens + sentence_tokens > self.max_chunk_size - context_tokens:
                if current_chunk:
                    # Save current chunk
                    full_chunk = context + current_chunk if chunks == [] else current_chunk
                    chunks.append({
                        'content': full_chunk.strip(),
                        'tokens': current_tokens + (context_tokens if chunks == [] else 0),
                        'title': title,
                        'url': url,
                        'chunk_id': len(chunks)
                    })
                    
                    # Start new chunk with overlap
                    overlap_text = ""
                    words = current_chunk.split()
                    overlap_words = words[-20:] if len(words) > 20 else words  # Last 20 words for overlap
                    overlap_text = " ".join(overlap_words)
                    
                    current_chunk = overlap_text + " " + sentence
                    current_tokens = self.count_tokens(current_chunk)
                else:
                    # Single sentence is too long, add it anyway
                    current_chunk = sentence
                    current_tokens = sentence_tokens
            else:
                current_chunk += " " + sentence
                current_tokens += sentence_tokens
        
        # Add the last chunk
        if current_chunk:
            full_chunk = context + current_chunk if chunks == [] else current_chunk
            chunks.append({
                'content': full_chunk.strip(),
                'tokens': current_tokens + (context_tokens if chunks == [] else 0),
                'title': title,
                'url': url,
                'chunk_id': len(chunks)
            })
        
        return chunks
    
    def process_documents(self, data_filepath="scraped_data/scraped_oncology_data.json"):
        # Load scraped data
        scraped_data = self.load_scraped_data(data_filepath)
        
        all_chunks = []
        processed_docs = 0
        
        for doc in scraped_data:
            # Prefer Hebrew content if available, otherwise use general content
            content = doc.get('hebrew_content', '') or doc.get('content', '')
            
            if not content or len(content.strip()) < 100:
                continue
            
            chunks = self.split_into_chunks(
                content, 
                title=doc.get('title', ''),
                url=doc.get('url', '')
            )
            
            all_chunks.extend(chunks)
            processed_docs += 1
            
            if processed_docs % 5 == 0:
                print(f"Processed {processed_docs} documents, created {len(all_chunks)} chunks")
        
        print(f"Total: Processed {processed_docs} documents into {len(all_chunks)} chunks")
        
        # Save processed chunks
        self.save_chunks(all_chunks)
        return all_chunks
    
    def save_chunks(self, chunks, filename="processed_chunks.json"):
        os.makedirs("scraped_data", exist_ok=True)
        filepath = os.path.join("scraped_data", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        print(f"Processed chunks saved to {filepath}")
        
        # Also save a sample for inspection
        sample_filepath = os.path.join("scraped_data", "chunk_samples.json")
        sample_chunks = chunks[:5] if len(chunks) > 5 else chunks
        
        with open(sample_filepath, 'w', encoding='utf-8') as f:
            json.dump(sample_chunks, f, ensure_ascii=False, indent=2)
        
        print(f"Sample chunks saved to {sample_filepath}")
    
    def get_processing_stats(self, chunks):
        total_tokens = sum(chunk['tokens'] for chunk in chunks)
        avg_tokens = total_tokens / len(chunks) if chunks else 0
        
        return {
            'total_chunks': len(chunks),
            'total_tokens': total_tokens,
            'average_tokens_per_chunk': avg_tokens,
            'max_tokens': max(chunk['tokens'] for chunk in chunks) if chunks else 0,
            'min_tokens': min(chunk['tokens'] for chunk in chunks) if chunks else 0
        }

def main():
    processor = DocumentProcessor()
    
    # Check if scraped data exists
    data_file = "scraped_data/scraped_oncology_data.json"
    if not os.path.exists(data_file):
        print(f"Scraped data file {data_file} not found. Run scraper.py first.")
        return
    
    # Process documents
    chunks = processor.process_documents(data_file)
    
    # Print stats
    stats = processor.get_processing_stats(chunks)
    print("\nProcessing Statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()