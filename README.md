# 🏥 Assuta Oncology RAG System

A Hebrew-language Retrieval-Augmented Generation (RAG) system for oncology information from Assuta Medical Centers. This system provides intelligent Q&A capabilities about cancer treatments, procedures, and services offered at Assuta.

## 📚 Features

- **Hebrew-language support** - Full RTL interface and Hebrew content processing
- **RAG-based Q&A** - Intelligent responses based on Assuta's oncology documentation
- **Comprehensive coverage** - Information about chemotherapy, radiation therapy, breast cancer, biopsies, and more
- **User-friendly interface** - Clean Streamlit web application
- **Source citations** - All answers include references to source documents

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone git@github.com:roy2392/assuta-rag.git
cd assuta-rag
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

4. Build the vector store:
```bash
python vector_store.py
```

5. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

## 📁 Project Structure

```
assuta-oncology-rag/
├── streamlit_app.py           # Main Streamlit application
├── rag_system.py              # RAG implementation and Q&A logic
├── vector_store.py            # Vector database management
├── document_processor.py      # Document processing utilities
├── html_cleaner.py           # HTML content extraction
├── scraper.py                # Web scraping utilities
├── advanced_scraper.py       # Advanced scraping with Playwright
├── sample_medical_data.py    # Sample medical content generator
├── run_pipeline.py           # Automated pipeline runner
├── chroma_db/                # ChromaDB vector storage
├── scraped_data/             # Processed document storage
│   ├── scraped_oncology_data.json
│   ├── processed_chunks.json
│   └── extraction_summary.json
├── assuta_onclogoy_scraped/  # Raw scraped HTML files
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── .gitignore               # Git ignore file
└── README.md                # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:
```env
OPENAI_API_KEY=your-openai-api-key-here
```

### System Components

1. **Vector Store**: ChromaDB for storing document embeddings
2. **LLM**: OpenAI GPT-4 for generating responses
3. **Embeddings**: OpenAI text-embedding-ada-002
4. **Frontend**: Streamlit web interface with Hebrew RTL support

## 📊 Current Data Coverage

The system includes comprehensive information about:
- 🏥 **Assuta Oncology Department** - Services, technologies, and multidisciplinary approach
- 💊 **Chemotherapy** - How it works, types, and side effects
- ☢️ **Radiation Therapy** - Treatment types and procedures
- 🎀 **Breast Cancer** - Diagnosis, treatment options, and surgery types
- 🔬 **Biopsy & Diagnosis** - Procedures, preparation, and follow-up

## 🔄 Updating Content

### To add new content:

1. Place HTML files in `assuta_onclogoy_scraped/`
2. Run the HTML cleaner:
```bash
python html_cleaner.py
```
3. Rebuild the vector store:
```bash
echo "y" | python vector_store.py
```

### To scrape new content:

```bash
# Basic scraping
python scraper.py

# Advanced scraping with JavaScript support
python advanced_scraper.py
```

## 💬 Usage Examples

The system can answer questions like:
- "מה זה כימותרפיה ואיך היא פועלת?"
- "איך מתבצע אבחון סרטן השד?"
- "מהן תופעות הלוואי של קרינה?"
- "מהם סוגי הביופסיות השונים?"
- "איך פועלת הגישה הרב-תחומית באסותא?"

## 🛠️ Development

### Running Tests
```bash
python rag_system.py test
```

### Interactive CLI
```bash
python rag_system.py chat
```

### Monitoring System Stats
```python
from rag_system import AssutaOncologyRAG
rag = AssutaOncologyRAG()
stats = rag.get_system_stats()
print(f"Documents: {stats['vector_store_documents']}")
```

## 📝 API Usage

### RAG System
```python
from rag_system import AssutaOncologyRAG

# Initialize
rag = AssutaOncologyRAG()

# Ask a question
result = rag.ask("מה זה כימותרפיה?")
print(result['response'])
print(result['citations'])
```

### Vector Store
```python
from vector_store import VectorStore

# Initialize
vs = VectorStore()

# Search
results = vs.search("סרטן השד", n_results=5)

# Get stats
stats = vs.get_collection_stats()
```

## 🎯 Features in Detail

### Streamlit Interface
- Full Hebrew RTL support
- Topic-based example questions
- Real-time document count display
- Citation expandable sections
- Clean, medical-focused design

### RAG System
- Context-aware responses
- Multi-document retrieval
- Hebrew-optimized prompts
- Source tracking and citations
- Medical terminology handling

## 🔍 Troubleshooting

### Common Issues:

1. **System shows "not ready"**
   - Run `python vector_store.py` to rebuild the database
   - Refresh the browser page

2. **OpenAI API errors**
   - Verify your API key in `.env`
   - Check API usage limits

3. **Empty responses**
   - Ensure vector store has data: `python -c "from vector_store import VectorStore; print(VectorStore().get_collection_stats())"`
   - Rebuild if needed

4. **Streamlit errors**
   - Clear cache: `streamlit cache clear`
   - Restart app: `streamlit run streamlit_app.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is for educational and research purposes. All medical content belongs to Assuta Medical Centers.

## ⚠️ Disclaimer

**IMPORTANT**: This system provides general medical information for educational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers at Assuta for personal medical concerns.

## 🆘 Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/roy2392/assuta-rag)
- Contact the maintainer

## 🚦 Project Status

✅ **Active** - System is fully functional with 5 comprehensive medical documents

---
Built with ❤️ for improving healthcare information accessibility in Hebrew