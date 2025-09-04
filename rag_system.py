import os
from openai import OpenAI
from vector_store import VectorStore
from typing import List, Dict
import json

class AssutaOncologyRAG:
    def __init__(self):
        # Initialize OpenAI client
        from dotenv import load_dotenv
        load_dotenv()
        
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize vector store
        self.vector_store = VectorStore()
        
        # System prompt in Hebrew
        self.system_prompt = """
אתה עוזר וירטואלי מומחה באונקולוגיה של בית החולים אסותא. תפקידך לענות על שאלות בעברית על נושאי אונקולוגיה בהתבסס על המידע הרפואי המפורט של אסותא.

המידע שברשותך כולל:
• המחלקה האונקולוגית של אסותא - שירותים כלליים וגישה רב-תחומית
• טיפולים אונקולוגיים מתקדמים - כימותרפיה, קרינה, ניתוחים
• טיפול בסרטן השד - אבחון, ניתוחים, טיפולים משלימים
• ביופסיות ואבחון - סוגים שונים של הליכי אבחון
• טיפול קרינתי (רדיותרפיה) - סוגים ושיטות מתקדמות

הנחיות חשובות:
1. ענה תמיד בעברית בלבד ובצורה מפורטת ומועילה
2. השתמש במידע הספציפי מהמסמכים של אסותא
3. תן תשובות מקיפות ומעשיות המבוססות על הידע הרפואי שברשותך
4. כלול פרטים רלוונטיים על תהליכים, טיפולים ושירותים
5. הסבר מונחים רפואיים באופן מובן למטופלים
6. כלול המלצה לפנות לצוות הרפואי לייעוץ אישי בסוף התשובה
7. שמור על טון מקצועי, אכפתי ומעודד
8. אל תיתן ייעוץ רפואי אישי ספציפי - רק מידע כללי וחינוכי
9. אם השאלה לא קשורה לאונקולוגיה, הסבר שאתה מתמחה באונקולוגיה של אסותא

דוגמאות לתשובות איכותיות:
- "על פי המידע של אסותא, טיפול כימותרפי מתבצע ב... ותופעות הלוואי כוללות..."
- "במחלקה האונקולוגית של אסותא מתבצעת גישה רב-תחומית הכוללת..."
- "תהליך הביופסיה באסותא כולל את השלבים הבאים..."

זכור: תן תשובות עשירות בתוכן המבוססות על המידע המפורט שברשותך מאסותא.
"""
    
    def retrieve_relevant_content(self, query: str, n_results: int = 5) -> List[Dict]:
        """Retrieve relevant documents from vector store"""
        return self.vector_store.search(query, n_results)
    
    def format_context(self, retrieved_docs: List[Dict]) -> tuple[str, List[Dict]]:
        """Format retrieved documents into context for the LLM and return citation info"""
        if not retrieved_docs:
            return "לא נמצא מידע רלוונטי במאגר המסמכים של אסותא.", []
        
        context = "מידע רלוונטי ממאגר המסמכים של אסותא:\n\n"
        citations = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            title = doc['metadata'].get('title', 'ללא כותרת')
            url = doc['metadata'].get('url', '')
            content = doc['content']
            score = doc['relevance_score']
            
            context += f"מסמך {i} (רלוונטיות: {score:.2f}):\n"
            context += f"כותרת: {title}\n"
            context += f"תוכן: {content}\n\n"
            
            # Store citation info with content excerpt
            # Extract a relevant excerpt (first 150 characters of content)
            content_excerpt = content.replace('\n', ' ').strip()
            if len(content_excerpt) > 150:
                content_excerpt = content_excerpt[:150] + "..."
            
            citations.append({
                'number': i,
                'title': title,
                'url': url,
                'score': score,
                'excerpt': content_excerpt,
                'full_content': content
            })
        
        return context, citations
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response using OpenAI with context"""
        
        user_prompt = f"""
שאלה: {query}

מידע רקע:
{context}

אנא ענה על השאלה בעברית בהתבסס על המידע שסופק. 

הוראות חשובות:
1. כאשר אתה מסתמך על מידע ממסמך מסוים, הוסף הפניה בסגנון [מסמך 1] או [מסמכים 1,2] 
2. הוסף הפניות אלו ישירות בטקסט ליד המידע הרלוונטי
3. אם המידע אינו מספיק, אמר זאת בבירור והמלץ לפנות לצוות הרפואי של אסותא
4. שמור על טון מקצועי ואכפתי

דוגמה לתשובה עם הפניות:
"כימותרפיה היא טיפול באמצעות תרופות [מסמך 1]. הטיפול יכול להיות ניתן בדרכים שונות [מסמך 2]..."
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"מצטער, אירעה שגיאה בעת יצירת התשובה: {str(e)}. אנא פנה לצוות הרפואי של אסותא לקבלת מידע מדויק."
    
    def ask(self, query: str, debug: bool = False) -> Dict:
        """Main method to ask a question and get an answer"""
        
        # Retrieve relevant documents
        retrieved_docs = self.retrieve_relevant_content(query)
        
        # Format context and get citations
        context, citations = self.format_context(retrieved_docs)
        
        # Generate response
        response = self.generate_response(query, context)
        
        result = {
            'query': query,
            'response': response,
            'sources_used': len(retrieved_docs),
            'citations': citations
        }
        
        if debug:
            result['retrieved_documents'] = retrieved_docs
            result['context'] = context
        
        return result
    
    def get_system_stats(self):
        """Get system statistics"""
        vector_stats = self.vector_store.get_collection_stats()
        return {
            'vector_store_documents': vector_stats['total_documents'],
            'collection_name': vector_stats['collection_name'],
            'system_status': 'ready' if vector_stats['total_documents'] > 0 else 'needs_data'
        }

def interactive_chat():
    """Interactive chat interface"""
    rag = AssutaOncologyRAG()
    
    print("🏥 ברוכים הבאים לעוזר האונקולוגיה של אסותא")
    print("💬 שאלו אותי כל שאלה על טיפולי אונקולוגיה באסותא")
    print("🚪 כתבו 'יציאה' או 'exit' להפסקת השיחה")
    print("📊 כתבו 'סטטיסטיקות' לראיית פרטי המערכת")
    print("-" * 50)
    
    # Check system status
    stats = rag.get_system_stats()
    if stats['system_status'] != 'ready':
        print("⚠️ המערכת לא מוכנה. יש להריץ תחילה את vector_store.py להכנת מאגר הנתונים.")
        return
    
    print(f"✅ המערכת מוכנה עם {stats['vector_store_documents']} מסמכים")
    print()
    
    while True:
        try:
            query = input("🔍 שאלתך: ").strip()
            
            if not query:
                continue
                
            if query.lower() in ['יציאה', 'exit', 'quit']:
                print("👋 להתראות!")
                break
                
            if query.lower() in ['סטטיסטיקות', 'stats']:
                stats = rag.get_system_stats()
                print(f"📊 סטטיסטיקות המערכת:")
                print(f"   מסמכים במאגר: {stats['vector_store_documents']}")
                print(f"   שם האוסף: {stats['collection_name']}")
                print(f"   סטטוס: {stats['system_status']}")
                continue
            
            print("🤔 חושב...")
            result = rag.ask(query)
            
            print(f"\n💡 תשובה:")
            print(result['response'])
            print(f"\n📚 מקורות שנעשה בהם שימוש: {result['sources_used']}")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 להתראות!")
            break
        except Exception as e:
            print(f"❌ שגיאה: {str(e)}")

def test_rag():
    """Test the RAG system with sample questions"""
    rag = AssutaOncologyRAG()
    
    test_questions = [
        "מה זה כימותרפיה?",
        "איך מתבצע טיפול בסרטן השד באסותא?",
        "מה ההבדל בין טיפול קרינתי לכימותרפיה?",
        "איך מתכוננים לביופסיה?",
        "מה הם תופעות הלוואי של טיפולי אונקולוגיה?"
    ]
    
    print("🧪 בדיקת המערכת עם שאלות דוגמה:")
    print("-" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. שאלה: {question}")
        result = rag.ask(question)
        print(f"תשובה: {result['response'][:200]}...")
        print(f"מקורות: {result['sources_used']}")

def main():
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_rag()
        elif sys.argv[1] == "chat":
            interactive_chat()
        else:
            print("Usage: python rag_system.py [test|chat]")
    else:
        interactive_chat()

if __name__ == "__main__":
    main()