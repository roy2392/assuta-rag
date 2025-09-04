#!/usr/bin/env python3
"""
Complete pipeline runner for Assuta Oncology RAG system
Run this script to build the complete system from scratch
"""

import os
import sys
import time
from pathlib import Path

def print_step(step_num, total_steps, description):
    print(f"\n{'='*60}")
    print(f"Step {step_num}/{total_steps}: {description}")
    print('='*60)

def run_command(description, module_name, function_name=None):
    print(f"🔄 {description}...")
    
    try:
        if function_name:
            exec(f"from {module_name} import {function_name}; {function_name}()")
        else:
            exec(f"import {module_name}")
        print(f"✅ {description} - הושלם בהצלחה")
        return True
    except Exception as e:
        print(f"❌ {description} - נכשל: {str(e)}")
        return False

def check_requirements():
    """Check if all required packages are installed"""
    print("🔍 בודק חבילות נדרשות...")
    
    required_packages = [
        'openai', 'bs4', 'requests', 'chromadb', 
        'langchain', 'streamlit', 'selenium', 'pandas', 'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ חבילות חסרות: {', '.join(missing_packages)}")
        print("💡 הריצו: pip install -r requirements.txt")
        return False
    
    print("✅ כל החבילות הנדרשות מותקנות")
    return True

def check_env_file():
    """Check if .env file exists and has OpenAI API key"""
    if not os.path.exists('.env'):
        print("❌ קובץ .env לא נמצא")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
        if 'OPENAI_API_KEY=' not in content or 'sk-' not in content:
            print("❌ מפתח OpenAI API לא נמצא בקובץ .env")
            return False
    
    print("✅ קובץ .env וחבילות נמצאו")
    return True

def main():
    print("🏥 מערכת RAG לאונקולוגיה של אסותא")
    print("🚀 הורדת נתונים ובניית מערכת שלמה")
    
    # Check prerequisites
    print_step(0, 5, "בדיקת דרישות מוקדמות")
    
    if not check_requirements():
        print("⛔ אנא התקינו את החבילות הנדרשות לפני המשך")
        return
    
    if not check_env_file():
        print("⛔ אנא הגדירו את קובץ .env עם מפתח OpenAI API")
        return
    
    print("✅ כל הדרישות המוקדמות מתקיימות")
    
    # Step 1: Scrape data
    print_step(1, 4, "איסוף נתונים מאתר אסותא")
    
    try:
        from scraper import main as scrape_main
        scrape_main()
        
        # Check if data was scraped
        if not os.path.exists("scraped_data/scraped_oncology_data.json"):
            raise Exception("לא נוצר קובץ נתונים")
            
        print("✅ איסוף נתונים הושלם")
        
    except Exception as e:
        print(f"❌ איסוף נתונים נכשל: {str(e)}")
        print("💡 נסו להריץ ידנית: python scraper.py")
        return
    
    # Step 2: Process documents
    print_step(2, 4, "עיבוד מסמכים וחלוקה לחלקים")
    
    try:
        from document_processor import main as process_main
        process_main()
        
        # Check if processed data exists
        if not os.path.exists("scraped_data/processed_chunks.json"):
            raise Exception("לא נוצר קובץ חלקים מעובדים")
            
        print("✅ עיבוד מסמכים הושלם")
        
    except Exception as e:
        print(f"❌ עיבוד מסמכים נכשל: {str(e)}")
        print("💡 נסו להריץ ידנית: python document_processor.py")
        return
    
    # Step 3: Build vector store
    print_step(3, 4, "בניית מאגר וקטורים")
    
    try:
        from vector_store import build_vector_store
        vector_store = build_vector_store()
        
        if vector_store is None:
            raise Exception("נכשל בניית מאגר וקטורים")
            
        # Test vector store
        stats = vector_store.get_collection_stats()
        if stats['total_documents'] == 0:
            raise Exception("מאגר הוקטורים ריק")
            
        print(f"✅ מאגר וקטורים נבנה בהצלחה עם {stats['total_documents']} מסמכים")
        
    except Exception as e:
        print(f"❌ בניית מאגר וקטורים נכשלה: {str(e)}")
        print("💡 נסו להריץ ידנית: python vector_store.py")
        return
    
    # Step 4: Test the system
    print_step(4, 4, "בדיקת המערכת")
    
    try:
        from rag_system import AssutaOncologyRAG
        
        rag = AssutaOncologyRAG()
        
        # Test with a simple query
        test_query = "מה זה כימותרפיה?"
        result = rag.ask(test_query)
        
        if not result['response'] or 'שגיאה' in result['response']:
            raise Exception("התשובה אינה תקינה")
            
        print(f"✅ המערכת עובדת! נבדקה עם השאלה: '{test_query}'")
        print(f"📊 מקורות שנמצאו: {result['sources_used']}")
        
    except Exception as e:
        print(f"❌ בדיקת המערכת נכשלה: {str(e)}")
        print("💡 נסו להריץ ידנית: python rag_system.py test")
        return
    
    # Success message
    print("\n" + "🎉" * 60)
    print("🎉 המערכת נבנתה בהצלחה!")
    print("🎉" * 60)
    
    print("\n🚀 כיצד להשתמש במערכת:")
    print("1. שיחה מסוף:      python rag_system.py chat")
    print("2. ממשק וב:        streamlit run streamlit_app.py")
    print("3. בדיקת מערכת:    python rag_system.py test")
    
    print("\n📊 סטטיסטיקות המערכת:")
    try:
        stats = rag.get_system_stats()
        print(f"   📄 מסמכים: {stats['vector_store_documents']}")
        print(f"   💾 מאגר: {stats['collection_name']}")
        print(f"   ✅ סטטוס: {stats['system_status']}")
    except:
        print("   ❓ לא ניתן לטעון סטטיסטיקות")
    
    print("\n⚠️  זכרו: המערכת נועדה למידע בלבד ואינה תחליף לייעוץ רפואי אישי")

if __name__ == "__main__":
    main()