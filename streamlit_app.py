import streamlit as st
import sys
import os
from rag_system import AssutaOncologyRAG

# Configure Streamlit page
st.set_page_config(
    page_title="עוזר אונקולוגיה אסותא",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Complete RTL support for Hebrew
st.markdown("""
<style>
    /* RTL for text inputs */
    .stTextInput > div > div > input {
        direction: rtl;
        text-align: right;
    }
    .stTextArea > div > div > textarea {
        direction: rtl;
        text-align: right;
    }
    
    /* RTL for chat input */
    .stChatInput > div > div > input {
        direction: rtl;
        text-align: right;
    }
    
    /* RTL for chat messages */
    .stChatMessage {
        direction: rtl;
        text-align: right;
    }
    
    /* RTL for all text content */
    .stMarkdown {
        direction: rtl;
        text-align: right;
    }
    
    /* RTL for expanders (citations) */
    .stExpander {
        direction: rtl;
        text-align: right;
    }
    
    /* RTL for captions */
    .stCaption {
        direction: rtl;
        text-align: right;
    }
    
    /* RTL for sidebar content */
    .stSidebar .stMarkdown {
        direction: rtl;
        text-align: right;
    }
    
    /* RTL for main content */
    .main .stMarkdown {
        direction: rtl;
        text-align: right;
    }
    
    /* RTL for titles */
    h1, h2, h3, h4, h5, h6 {
        direction: rtl;
        text-align: right;
    }
    
    /* RTL for paragraphs */
    p {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_rag_system():
    """Load the RAG system with caching"""
    try:
        rag = AssutaOncologyRAG()
        # Verify the system is properly loaded
        stats = rag.get_system_stats()
        print(f"RAG System loaded with {stats['vector_store_documents']} documents")
        return rag
    except Exception as e:
        st.error(f"Error loading RAG system: {str(e)}")
        return None

def main():
    # Header
    st.title("🏥 עוזר אונקולוגיה אסותא")
    st.markdown("**מידע רפואי מבוסס על תוכן אסותא באונקולוגיה**")
    
    # Sidebar
    with st.sidebar:
        st.header("📊 מידע על המערכת")
        
        # Load RAG system
        rag = load_rag_system()
        
        if rag is None:
            st.error("❌ המערכת אינה זמינה")
            st.stop()
        
        # Get system stats
        try:
            stats = rag.get_system_stats()
            
            # Display document count prominently
            st.success(f"📚 **{stats['vector_store_documents']} מסמכים במאגר**")
            st.metric("סטטוס מערכת", "✅ פעילה" if stats['system_status'] == 'ready' else "❌ לא מוכנה")
            
            # Additional system info
            if stats['vector_store_documents'] > 0:
                st.info(f"המאגר כולל מידע מפורט מ־{stats['vector_store_documents']} נושאים מרכזיים באונקולוגיה של אסותא")
            
            if stats['system_status'] != 'ready':
                st.warning("⚠️ המערכת אינה מוכנה. יש להריץ תחילה את הסקריפטים הדרושים.")
                st.stop()
                
        except Exception as e:
            st.error(f"שגיאה בטעינת סטטיסטיקות: {str(e)}")
            st.stop()
        
        st.markdown("---")
        
        # Instructions
        st.subheader("📝 הוראות שימוש")
        st.markdown("""
        **איך להשתמש:**
        1. כתבו שאלה על אונקולוגיה בעברית
        2. לחצו על "שלח" או Enter
        3. קבלו תשובה מבוססת על מידע אסותא
        """)
        
        # Example questions by topic
        st.subheader("💡 דוגמאות לשאלות לפי נושא")
        
        with st.expander("🏥 כללי - המחלקה האונקולוגית"):
            st.markdown("""
            - איך פועלת הגישה הרב-תחומית באסותא?
            - מהן הטכנולוגיות המתקדמות במחלקה?
            - איך נבנה צוות הטיפול האונקולוגי?
            """)
        
        with st.expander("💊 כימותרפיה"):
            st.markdown("""
            - מה זה כימותרפיה ואיך היא פועלת?
            - מהן תופעות הלוואי של כימותרפיה?
            - מהם סוגי הכימותרפיה השונים?
            """)
        
        with st.expander("☢️ טיפול קרינתי"):
            st.markdown("""
            - מה זה טיפול קרינתי ואיך הוא עובד?
            - מהם סוגי הטיפול הקרינתי?
            - מהן תופעות הלוואי של קרינה?
            """)
        
        with st.expander("🎀 סרטן השד"):
            st.markdown("""
            - איך מתבצע אבחון סרטן השד?
            - מהן אפשרויות הטיפול בסרטן השד?
            - מהם סוגי הניתוחים בסרטן השד?
            """)
        
        with st.expander("🔬 ביופסיות ואבחון"):
            st.markdown("""
            - מה זה ביופסיה ואיך מתכוننים אליה?
            - מהם סוגי הביופסיות השונים?
            - מה קורה לאחר הביופסיה?
            """)
        
        st.markdown("---")
        st.markdown("**⚠️ הצהרת אחריות:**")
        st.caption("המידע נועד להעשרת ידע בלבד ואינו תחליף לייעוץ רפואי אישי")
        
        # Clear chat button
        if st.button("🧹 נקה שיחה"):
            st.session_state.clear()
            st.rerun()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
        # Welcome message
        welcome_msg = """
🏥 שלום! אני עוזר וירטואלי באונקולוגיה של בית החולים אסותא.

אני כאן לעזור לכם עם מידע על טיפולי אונקולוגיה, תהליכים רפואיים והליכים באסותא.

⚠️ חשוב לזכור: המידע שאני מספק הוא למטרות חינוכיות בלבד ואינו תחליף לייעוץ רפואי אישי. 
תמיד התייעצו עם הצוות הרפואי של אסותא לקבלת טיפול מותאם אישית.

מה תרצו לדעת על אונקולוגיה באסותא?
"""
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Display citations if available
            if message["role"] == "assistant" and "citations" in message and message["citations"]:
                with st.expander("📚 מקורות המידע"):
                    for i, citation in enumerate(message["citations"][:3]):
                        title = citation.get('title', 'מקור')
                        excerpt = citation.get('excerpt', '')
                        url = citation.get('url', '')
                        score = citation.get('score', 0)
                        
                        st.markdown(f"**{i+1}. {title}**")
                        if excerpt:
                            st.caption(f"תוכן: {excerpt}")
                        if url:
                            st.caption(f"מקור: {url}")
                        st.caption(f"רלוונטיות: {score:.2f}")
                        if i < len(message["citations"]) - 1:
                            st.divider()
    
    # Chat input
    if prompt := st.chat_input("הקלד שאלה על אונקולוגיה..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("חושב..."):
                try:
                    result = rag.ask(prompt)
                    response = result['response']
                    citations = result.get('citations', [])
                    
                    st.write(response)
                    
                    # Display citations
                    if citations:
                        with st.expander("📚 מקורות המידע"):
                            for i, citation in enumerate(citations[:3]):
                                title = citation.get('title', 'מקור')
                                excerpt = citation.get('excerpt', '')
                                url = citation.get('url', '')
                                score = citation.get('score', 0)
                                
                                st.markdown(f"**{i+1}. {title}**")
                                if excerpt:
                                    st.caption(f"תוכן: {excerpt}")
                                if url:
                                    st.caption(f"מקור: {url}")
                                st.caption(f"רלוונטיות: {score:.2f}")
                                if i < len(citations) - 1:
                                    st.divider()
                    
                    # Store message with citations
                    message_data = {
                        "role": "assistant", 
                        "content": response,
                        "citations": citations
                    }
                    
                except Exception as e:
                    error_msg = f"❌ מצטער, אירעה שגיאה: {str(e)}\nאנא נסו שוב או פנו לצוות הרפואי של אסותא."
                    st.write(error_msg)
                    message_data = {
                        "role": "assistant", 
                        "content": error_msg
                    }
        
        # Add assistant response to chat history
        st.session_state.messages.append(message_data)

if __name__ == "__main__":
    main()