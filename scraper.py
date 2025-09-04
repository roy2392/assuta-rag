import requests
from bs4 import BeautifulSoup
import os
import json
import time
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class AssutaScraper:
    def __init__(self):
        self.base_url = "https://www.assuta.co.il"
        self.oncology_base = "https://www.assuta.co.il/services/oncology/"
        self.visited_urls = set()
        self.scraped_data = []
        self.setup_driver()
        
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
    
    def get_page_content(self, url):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract main content
            content_selectors = [
                '.main-content',
                '.content',
                'main',
                'article',
                '.page-content',
                '.entry-content'
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.find('body')
            
            # Extract text content
            text_content = main_content.get_text(separator=' ', strip=True) if main_content else ""
            
            # Clean up extra whitespace
            text_content = ' '.join(text_content.split())
            
            # Extract title
            title_element = soup.find('title')
            title = title_element.get_text().strip() if title_element else ""
            
            # Extract Hebrew content specifically
            hebrew_paragraphs = []
            for p in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                text = p.get_text().strip()
                if self.contains_hebrew(text) and len(text) > 10:
                    hebrew_paragraphs.append(text)
            
            return {
                'url': url,
                'title': title,
                'content': text_content,
                'hebrew_content': '\n'.join(hebrew_paragraphs),
                'length': len(text_content)
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def contains_hebrew(self, text):
        hebrew_chars = [char for char in text if '\u0590' <= char <= '\u05FF']
        return len(hebrew_chars) > 3
    
    def find_oncology_links(self, soup, current_url):
        links = set()
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(current_url, href)
            
            # Check if link is related to oncology and within Assuta domain
            if (self.base_url in full_url and 
                ('oncology' in full_url.lower() or 
                 'onkolog' in full_url.lower() or
                 'cancer' in full_url.lower() or
                 'sartan' in full_url.lower())):
                links.add(full_url)
        
        return links
    
    def scrape_oncology_pages(self, max_pages=50):
        urls_to_visit = [self.oncology_base]
        
        while urls_to_visit and len(self.visited_urls) < max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue
                
            print(f"Scraping: {current_url}")
            self.visited_urls.add(current_url)
            
            # Get page content
            page_data = self.get_page_content(current_url)
            
            if page_data and page_data['length'] > 100:
                self.scraped_data.append(page_data)
                print(f"Scraped {len(page_data['content'])} characters from {current_url}")
                
                # Find additional oncology links
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                new_links = self.find_oncology_links(soup, current_url)
                
                for link in new_links:
                    if link not in self.visited_urls and link not in urls_to_visit:
                        urls_to_visit.append(link)
            
            time.sleep(1)  # Be respectful to the server
        
        print(f"Completed scraping {len(self.scraped_data)} pages")
        return self.scraped_data
    
    def save_data(self, filename="scraped_oncology_data.json"):
        os.makedirs("scraped_data", exist_ok=True)
        filepath = os.path.join("scraped_data", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, ensure_ascii=False, indent=2)
        
        print(f"Data saved to {filepath}")
    
    def close(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    scraper = AssutaScraper()
    try:
        data = scraper.scrape_oncology_pages(max_pages=30)
        scraper.save_data()
        print(f"Successfully scraped {len(data)} oncology pages")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()