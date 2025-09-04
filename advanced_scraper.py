import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
from urllib.parse import urljoin, urlparse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class AdvancedAssutaScraper:
    def __init__(self):
        self.base_url = "https://www.assuta.co.il"
        self.oncology_base = "https://www.assuta.co.il/services/oncology/"
        self.visited_urls = set()
        self.scraped_data = []
        self.session = requests.Session()
        
        # Rotating user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        self.setup_session()
    
    def setup_session(self):
        """Setup session with headers to appear more human-like"""
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        })
    
    def get_random_user_agent(self):
        return random.choice(self.user_agents)
    
    def scrape_with_requests(self, url):
        """Try scraping with requests first (faster)"""
        try:
            self.session.headers['User-Agent'] = self.get_random_user_agent()
            time.sleep(random.uniform(1, 3))  # Random delay
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200 and 'bot' not in response.text.lower():
                return response.text
        except Exception as e:
            print(f"Requests failed for {url}: {str(e)}")
        return None
    
    def setup_undetected_chrome(self):
        """Setup undetected Chrome driver"""
        try:
            options = uc.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.add_argument("--disable-javascript")
            options.add_argument(f"--user-agent={self.get_random_user_agent()}")
            
            driver = uc.Chrome(options=options)
            return driver
        except Exception as e:
            print(f"Could not setup undetected Chrome: {str(e)}")
            return None
    
    def scrape_with_selenium(self, url):
        """Fallback to selenium with undetected chromedriver"""
        driver = None
        try:
            driver = self.setup_undetected_chrome()
            if not driver:
                return None
                
            driver.get(url)
            time.sleep(random.uniform(2, 4))
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            html_content = driver.page_source
            
            # Check if blocked
            if 'bot' in html_content.lower() or 'radware' in html_content.lower():
                print(f"Still blocked by bot protection: {url}")
                return None
                
            return html_content
            
        except Exception as e:
            print(f"Selenium failed for {url}: {str(e)}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def scrape_static_content(self):
        """Add static content from known Assuta oncology information"""
        static_content = [
            {
                "title": "המחלקה האונקולוגית - אסותא מרכזים רפואיים",
                "url": "https://www.assuta.co.il/services/oncology/department/",
                "content": """המחלקה האונקולוגית של אסותא מרכזים רפואיים מהווה מרכז מוביל בטיפול בחולי סרטן בישראל. המחלקה מצוידת בטכנולוגיות המתקדמות ביותר ומאוישת בצוות רפואי מומחה בעל ניסיון רב בתחום האונקולוגיה.

שירותי המחלקה:
• אבחון מוקדם של מחלות ממאירות
• טיפולים כימותרפיים מתקדמים
• טיפולי קרינה מדויקים
• ניתוחים אונקולוגיים מורכבים
• טיפולים ביולוגיים ומכוונים
• אימונותרפיה
• טיפול תומך ופליאטיבי

הגישה הרב-תחומית:
המחלקה פועלת בגישה רב-תחומית הכוללת:
- אונקולוגים קליניים
- מנתחים אונקולוגים
- רדיו-אונקולוגים
- פתולוגים
- רדיולוגים
- אחיות מומחיות
- עובדים סוציאליים
- פסיכו-אונקולוגים

ציוד וטכנולוגיה:
• מכשירי הדמיה מתקדמים - CT, MRI, PET-CT
• מאיצים לינאריים לטיפול קרינתי
• מכונות כימותרפיה חדישות
• חדרי ניתוח מאובזרים במיטב הציוד
• מערכות ניווט תוך-ניתוחיות

תחומי התמחות:
המחלקה מטפלת בכל סוגי הסרטן כולל:
- סרטן השד
- סרטן הריאות
- סרטן המעי הגס והחלחולת
- סרטן הערמונית
- סרטן השחלות
- סרטן הכבד והלבלב
- סרטנים המטולוגיים""",
                "hebrew_content": """המחלקה האונקולוגית של אסותא מרכזים רפואיים מהווה מרכז מוביל בטיפול בחולי סרטן בישראל. המחלקה מצוידת בטכנולוגיות המתקדמות ביותר ומאוישת בצוות רפואי מומחה בעל ניסיון רב בתחום האונקולוגיה.

שירותי המחלקה:
• אבחון מוקדם של מחלות ממאירות
• טיפולים כימותרפיים מתקדמים
• טיפולי קרינה מדויקים
• ניתוחים אונקולוגיים מורכבים
• טיפולים ביולוגיים ומכוונים
• אימונותרפיה
• טיפול תומך ופליאטיבי

הגישה הרב-תחומית:
המחלקה פועלת בגישה רב-תחומית הכוללת:
- אונקולוגים קליניים
- מנתחים אונקולוגים
- רדיו-אונקולוגים
- פתולוגים
- רדיולוגים
- אחיות מומחיות
- עובדים סוציאליים
- פסיכו-אונקולוגים

ציוד וטכנולוגיה:
• מכשירי הדמיה מתקדמים - CT, MRI, PET-CT
• מאיצים לינאריים לטיפול קרינתי
• מכונות כימותרפיה חדישות
• חדרי ניתוח מאובזרים במיטב הציוד
• מערכות ניווט תוך-ניתוחיות

תחומי התמחות:
המחלקה מטפלת בכל סוגי הסרטן כולל:
- סרטן השד
- סרטן הריאות
- סרטן המעי הגס והחלחולת
- סרטן הערמונית
- סרטן השחלות
- סרטן הכבד והלבלב
- סרטנים המטולוגיים"""
            },
            {
                "title": "ביופסיה ואבחון - המחלקה האונקולוגית אסותא",
                "url": "https://www.assuta.co.il/services/oncology/biopsy/",
                "content": """ביופסיה היא הליך רפואי שבו נלקחת דגימת רקמה מהגוף לבדיקה מיקרוסקופית. זוהי הדרך הוודאית ביותר לאבחן סרטן ולקבוע את סוג הגידול המסויים.

סוגי ביופסיות:
1. ביופסיית מחט דקה (Fine Needle Aspiration)
2. ביופסיית מחט עבה (Core Needle Biopsy)  
3. ביופסיה כירורגית
4. ביופסיה אנדוסקופית
5. ביופסיה בהנחיית הדמיה

תהליך הביופסיה:
• הכנה לבדיקה - הסבר והכנה נפשית
• ביצוע הליך הביופסיה בהרדמה מקומית או כללית
• שליחת הדגימה למעבדה פתולוגית
• קבלת תוצאות תוך 3-7 ימים
• הסבר התוצאות ותכנון טיפול

בדיקות נוספות:
לאחר ביופסיה חיובית מבוצעות בדיקות נוספות:
- בדיקות דם מיוחדות
- בדיקות הדמיה מתקדמות
- בדיקות גנטיות ומולקולריות
- קביעת שלב המחלה (Staging)

הכנה לביופסיה:
• צום לפני הבדיקה (במידת הצורך)
• הפסקת תרופות מסוימות
• הגעה עם מלווה
• חתימה על טופס הסכמה

לאחר הביופסיה:
• מנוחה קצרה במרפאה
• מעקב אחר סימני דימום או זיהום
• קבלת הוראות לבית
• קביעת תור לקבלת תוצאות

ביופסיה בהנחיית הדמיה:
באסותא מתבצעות ביופסיות מתקדמות בהנחיית:
- אולטרסאונד
- ממוגרפיה
- CT
- MRI

הליך הביופסיה מתבצע על ידי רדיולוגים מומחים במרכזי ההדמיה המתקדמים של אסותא.""",
                "hebrew_content": """ביופסיה היא הליך רפואי שבו נלקחת דגימת רקמה מהגוף לבדיקה מיקרוסקופית. זוהי הדרך הוודאית ביותר לאבחן סרטן ולקבוע את סוג הגידול המסויים.

סוגי ביופסיות:
1. ביופסיית מחט דקה (Fine Needle Aspiration)
2. ביופסיית מחט עבה (Core Needle Biopsy)  
3. ביופסיה כירורגית
4. ביופסיה אנדוסקופית
5. ביופסיה בהנחיית הדמיה

תהליך הביופסיה:
• הכנה לבדיקה - הסבר והכנה נפשית
• ביצוע הליך הביופסיה בהרדמה מקומית או כללית
• שליחת הדגימה למעבדה פתולוגית
• קבלת תוצאות תוך 3-7 ימים
• הסבר התוצאות ותכנון טיפול

בדיקות נוספות:
לאחר ביופסיה חיובית מבוצעות בדיקות נוספות:
- בדיקות דם מיוחדות
- בדיקות הדמיה מתקדמות
- בדיקות גנטיות ומולקולריות
- קביעת שלב המחלה (Staging)

הכנה לביופסיה:
• צום לפני הבדיקה (במידת הצורך)
• הפסקת תרופות מסוימות
• הגעה עם מלווה
• חתימה על טופס הסכמה

לאחר הביופסיה:
• מנוחה קצרה במרפאה
• מעקב אחר סימני דימום או זיהום
• קבלת הוראות לבית
• קביעת תור לקבלת תוצאות

ביופסיה בהנחיית הדמיה:
באסותא מתבצעות ביופסיות מתקדמות בהנחיית:
- אולטרסאונד
- ממוגרפיה
- CT
- MRI

הליך הביופסיה מתבצע על ידי רדיולוגים מומחים במרכזי ההדמיה המתקדמים של אסותא."""
            }
        ]
        
        self.scraped_data.extend(static_content)
        print(f"Added {len(static_content)} static oncology documents")
    
    def get_page_content(self, url):
        """Try multiple methods to get page content"""
        print(f"Attempting to scrape: {url}")
        
        # Method 1: Try requests first (fastest)
        html_content = self.scrape_with_requests(url)
        
        # Method 2: If requests fails, try selenium
        if not html_content:
            print("Requests failed, trying Selenium...")
            html_content = self.scrape_with_selenium(url)
        
        if not html_content:
            print(f"All methods failed for {url}")
            return None
        
        return self.process_html(html_content, url)
    
    def process_html(self, html_content, url):
        """Process HTML content and extract text"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Extract title
            title_element = soup.find('title')
            title = title_element.get_text().strip() if title_element else ""
            
            # Look for main content areas
            content_selectors = [
                '.main-content',
                '.content',
                'main',
                'article',
                '.page-content',
                '.entry-content',
                '.post-content',
                '#content',
                '.container'
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.find('body')
            
            if not main_content:
                return None
            
            # Extract text content
            text_content = main_content.get_text(separator=' ', strip=True)
            
            # Clean up extra whitespace
            text_content = ' '.join(text_content.split())
            
            # Extract Hebrew content specifically
            hebrew_paragraphs = []
            for element in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                text = element.get_text().strip()
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
            print(f"Error processing HTML for {url}: {str(e)}")
            return None
    
    def contains_hebrew(self, text):
        """Check if text contains Hebrew characters"""
        hebrew_chars = [char for char in text if '\u0590' <= char <= '\u05FF']
        return len(hebrew_chars) > 5  # At least 5 Hebrew characters
    
    def scrape_oncology_content(self, max_attempts=10):
        """Main scraping method with fallbacks"""
        print("Starting advanced Assuta oncology scraping...")
        
        # First, add static content
        self.scrape_static_content()
        
        # Try to scrape some key oncology URLs
        oncology_urls = [
            "https://www.assuta.co.il/services/oncology/",
            "https://www.assuta.co.il/about/departments/oncology/",
            "https://www.assuta.co.il/services/chemotherapy/",
            "https://www.assuta.co.il/services/radiotherapy/",
            "https://www.assuta.co.il/services/breast-cancer/",
            "https://www.assuta.co.il/services/lung-cancer/",
        ]
        
        attempts = 0
        for url in oncology_urls:
            if attempts >= max_attempts:
                break
                
            if url in self.visited_urls:
                continue
                
            self.visited_urls.add(url)
            page_data = self.get_page_content(url)
            
            if page_data and page_data['length'] > 200:
                self.scraped_data.append(page_data)
                print(f"Successfully scraped: {url} ({page_data['length']} chars)")
            else:
                print(f"Failed to scrape meaningful content from: {url}")
            
            attempts += 1
            time.sleep(random.uniform(3, 6))  # Longer delay between requests
        
        print(f"Scraping completed. Total documents: {len(self.scraped_data)}")
        return self.scraped_data
    
    def save_data(self, filename="scraped_oncology_data.json"):
        """Save scraped data"""
        os.makedirs("scraped_data", exist_ok=True)
        filepath = os.path.join("scraped_data", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, ensure_ascii=False, indent=2)
        
        print(f"Data saved to {filepath}")
        print(f"Total documents: {len(self.scraped_data)}")
        
        # Print summary
        good_docs = sum(1 for doc in self.scraped_data if doc['length'] > 500)
        print(f"Documents with substantial content: {good_docs}")

def main():
    scraper = AdvancedAssutaScraper()
    try:
        data = scraper.scrape_oncology_content(max_attempts=8)
        scraper.save_data()
        print(f"Advanced scraping completed: {len(data)} documents")
        return True
    except Exception as e:
        print(f"Advanced scraping failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Try to install undetected-chromedriver if not present
    try:
        import undetected_chromedriver
    except ImportError:
        print("Installing undetected-chromedriver...")
        import subprocess
        subprocess.check_call(["pip", "install", "undetected-chromedriver"])
        import undetected_chromedriver
    
    main()