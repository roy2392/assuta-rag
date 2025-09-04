#!/usr/bin/env python3
"""
HTML Cleaner for Assuta Oncology Content
Extracts relevant medical information from downloaded HTML files
"""

import os
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
import urllib.parse

class AssutaHTMLCleaner:
    def __init__(self, html_folder, output_folder="scraped_data"):
        self.html_folder = Path(html_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)
        
        # Medical content selectors - common patterns in medical websites
        self.content_selectors = [
            'main',
            '.content',
            '.article-content',
            '.page-content',
            '.medical-content',
            '.service-content',
            '#main-content',
            '.text-content',
            '.description',
            '.treatment-info'
        ]
        
        # Elements to remove completely
        self.remove_selectors = [
            'script',
            'style',
            'nav',
            'header',
            'footer',
            '.navigation',
            '.menu',
            '.sidebar',
            '.ads',
            '.advertisement',
            '.social-media',
            '.breadcrumb',
            '.footer-links',
            '.header-links',
            'noscript',
            '.cookie-notice',
            '.popup'
        ]

    def clean_html_file(self, html_file):
        """Clean a single HTML file and extract medical content"""
        try:
            print(f"Processing: {html_file.name}")
            
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for selector in self.remove_selectors:
                for element in soup.select(selector):
                    element.decompose()
            
            # Extract title
            title = self._extract_title(soup, html_file.name)
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Extract URL from filename
            url = self._extract_url_from_filename(html_file.name)
            
            if content.strip():
                return {
                    'title': title,
                    'url': url,
                    'content': content,
                    'file': html_file.name
                }
            else:
                print(f"⚠️  No content extracted from {html_file.name}")
                return None
                
        except Exception as e:
            print(f"❌ Error processing {html_file.name}: {str(e)}")
            return None

    def _extract_title(self, soup, filename):
        """Extract page title"""
        # Try multiple title sources
        title_sources = [
            soup.find('title'),
            soup.find('h1'),
            soup.select_one('.page-title'),
            soup.select_one('.article-title'),
            soup.select_one('.service-title')
        ]
        
        for source in title_sources:
            if source and source.get_text().strip():
                title = source.get_text().strip()
                # Clean title
                title = re.sub(r'\s+', ' ', title)
                title = title.replace(' - אסותא', '').strip()
                return title
        
        # Fallback: extract from filename
        return filename.replace('view-source_https___www.assuta.co.il_services_oncology_', '').\
               replace('.html', '').replace('_', ' ').title()

    def _extract_main_content(self, soup):
        """Extract the main medical content from the page"""
        content_parts = []
        
        # Remove unwanted elements first
        for selector in self.remove_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # Extract meaningful text content
        content_parts = self._extract_clean_text(soup)
        
        # Join all content
        full_content = '\n\n'.join(filter(None, content_parts))
        
        # Clean up the content
        full_content = self._clean_text(full_content)
        
        return full_content

    def _extract_clean_text(self, soup):
        """Extract clean text from soup, focusing on meaningful content"""
        content_parts = []
        
        # Look for Hebrew text patterns and meaningful content
        for element in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th']):
            text = element.get_text().strip()
            
            # Skip empty or very short text
            if len(text) < 15:
                continue
            
            # Skip navigation and non-medical content
            if self._is_navigation_text(text):
                continue
            
            # Skip HTML/CSS/JS patterns
            if any(pattern in text for pattern in ['<', '>', 'function(', 'var ', 'const ', 'javascript:', 'css', 'px', 'color:', 'margin:']):
                continue
            
            # Look for Hebrew content (medical text is likely in Hebrew)
            if self._contains_hebrew(text):
                # Clean and add meaningful text
                clean_text = self._clean_text_basic(text)
                if len(clean_text) > 20:  # Only meaningful content
                    content_parts.append(clean_text)
        
        return content_parts

    def _contains_hebrew(self, text):
        """Check if text contains Hebrew characters"""
        hebrew_pattern = re.compile(r'[\u0590-\u05FF]')
        return bool(hebrew_pattern.search(text))

    def _clean_text_basic(self, text):
        """Basic text cleaning"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        return text.strip()

    def _extract_structured_text(self, element):
        """Extract text while preserving structure"""
        content_parts = []
        
        # Process different HTML elements
        for elem in element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'li', 'span']):
            text = elem.get_text().strip()
            
            # Skip empty text or very short text
            if len(text) < 10:
                continue
            
            # Skip navigation-like text
            if self._is_navigation_text(text):
                continue
            
            # Add headers with formatting
            if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                content_parts.append(f"## {text}")
            elif elem.name == 'li':
                content_parts.append(f"• {text}")
            else:
                content_parts.append(text)
        
        return content_parts

    def _is_navigation_text(self, text):
        """Check if text is likely navigation or non-medical content"""
        navigation_keywords = [
            'דף הבית', 'צור קשר', 'אודות', 'תפריט', 'ניווט',
            'פייסבוק', 'טוויטר', 'לינקדאין', 'אינסטגרם',
            'קובץ עוגיות', 'מדיניות פרטיות', 'תקנון',
            'כל הזכויות שמורות', 'עוד באתר', 'קישורים'
        ]
        
        return any(keyword in text for keyword in navigation_keywords) or len(text) < 15

    def _clean_text(self, text):
        """Clean and normalize extracted text"""
        # Remove multiple whitespaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        
        # Remove extra punctuation
        text = re.sub(r'[•▪▫◦‣⁃]\s*', '• ', text)
        
        return text.strip()

    def _extract_url_from_filename(self, filename):
        """Convert filename back to URL"""
        if filename.startswith('view-source_'):
            url = filename.replace('view-source_', '')
            url = url.replace('.html', '')
            url = url.replace('___', '://')
            url = url.replace('__', '/')
            url = url.replace('_', '/')
            return urllib.parse.unquote(url)
        return filename

    def process_all_files(self):
        """Process all HTML files in the folder"""
        html_files = list(self.html_folder.glob('*.html'))
        
        if not html_files:
            print(f"❌ No HTML files found in {self.html_folder}")
            return []
        
        print(f"📁 Found {len(html_files)} HTML files")
        
        extracted_docs = []
        
        for html_file in html_files:
            doc = self.clean_html_file(html_file)
            if doc:
                extracted_docs.append(doc)
                print(f"✅ Extracted content from {html_file.name}")
            
        print(f"\n📊 Successfully processed {len(extracted_docs)} files")
        return extracted_docs

    def save_extracted_content(self, docs):
        """Save extracted content to JSON files"""
        if not docs:
            print("❌ No documents to save")
            return
        
        # Save raw extracted content
        raw_file = self.output_folder / 'raw_extracted_content.json'
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved raw content to {raw_file}")
        
        # Create processed chunks for RAG
        chunks = []
        chunk_id = 0
        
        for doc in docs:
            # Split content into manageable chunks
            content_chunks = self._split_content(doc['content'])
            
            for chunk in content_chunks:
                chunks.append({
                    'content': f"כותרת: {doc['title']}\nמקור: {doc['url']}\n\n{chunk}",
                    'title': doc['title'],
                    'url': doc['url'],
                    'chunk_id': chunk_id,
                    'tokens': len(chunk.split()) * 1.3  # Rough estimate for Hebrew
                })
                chunk_id += 1
        
        # Save processed chunks
        chunks_file = self.output_folder / 'processed_chunks.json'
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved {len(chunks)} chunks to {chunks_file}")
        
        # Create summary
        summary = {
            'total_files_processed': len(docs),
            'total_chunks_created': len(chunks),
            'files': [{'title': doc['title'], 'url': doc['url'], 'file': doc['file']} for doc in docs]
        }
        
        summary_file = self.output_folder / 'extraction_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Saved summary to {summary_file}")

    def _split_content(self, content, max_chunk_size=1000):
        """Split content into chunks suitable for RAG"""
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Rough word count for Hebrew (words * 1.3 for Hebrew characters)
            para_size = len(paragraph.split()) * 1.3
            
            if current_size + para_size > max_chunk_size and current_chunk:
                # Save current chunk
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_size = para_size
            else:
                current_chunk.append(paragraph)
                current_size += para_size
        
        # Add remaining chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks


def main():
    """Main function to run the HTML cleaner"""
    html_folder = "/Users/royzalta/Documents/GitHub/assuta-oncology-rag/assuta_onclogoy_scraped"
    
    print("🏥 Assuta Oncology HTML Cleaner")
    print("=" * 50)
    
    # Check if folder exists
    if not os.path.exists(html_folder):
        print(f"❌ HTML folder not found: {html_folder}")
        return
    
    # Initialize cleaner
    cleaner = AssutaHTMLCleaner(html_folder)
    
    # Process all HTML files
    docs = cleaner.process_all_files()
    
    if docs:
        # Save extracted content
        cleaner.save_extracted_content(docs)
        
        print("\n🎉 HTML cleaning completed successfully!")
        print(f"📊 Results:")
        print(f"   • Files processed: {len(docs)}")
        print(f"   • Output folder: {cleaner.output_folder}")
        print(f"   • Next step: Run 'python vector_store.py' to update the RAG system")
    else:
        print("❌ No content was extracted from HTML files")


if __name__ == "__main__":
    main()