# DynaBot - Instant Custom Chatbot Generator

A **multi-tenant platform** that lets users create their own AI chatbots in minutes. Upload documents, paste website URLs, or type information directly—DynaBot instantly generates custom chatbots with shareable links and QR codes.

## 🎯 What This Does

- **Multi-Tenant Chatbot Creator**: Each user creates their own branded chatbot from their data
- **Flexible Data Input**: Upload documents, crawl websites, or paste text directly
- **AI-Powered Answers**: Chatbots answer questions based on user-provided information using GPT-4o
- **Instant Sharing**: Generate shareable chatbot URLs and QR codes for easy distribution
- **Secure & Isolated**: Each user's data and chatbot is completely isolated and private
- **No Code Required**: Users upload data → system builds chatbot automatically

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Pinecone API key

### Common Use Cases

- **Customer Support**: Create a chatbot trained on your FAQ/help docs
- **Product Knowledge**: Embed product documentation for instant answers
- **Training Platform**: Generate chatbots from training materials
- **Research Assistance**: Upload research papers and ask questions
- **Internal Knowledge Base**: Create company-wide chatbots from documentation

### 1. Set Up Environment Variables

Edit `settings.json` with your API keys:

```json
{
    "openai_api_key": "your-openai-api-key-here",
    "pinecone_api_key": "your-pinecone-api-key-here"
}
```

### 2. Install Dependencies

```bash
# Activate virtual environment (if using)
.\env\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

### 3. Ingest Documents

Before you can ask questions, you need to process your documents:

```bash
# Standard ingestion (with full processing)
python run_ingest.py

# Or: Only process embeddings without metadata
python run_embed_only.py

# Or: Standalone ingestion (no external dependencies)
python run_ingest_standalone.py
```

### 4. Run the Application

```bash
# Start the FastAPI server
python main.py
```

The API will be available at: **http://localhost:8000**

Access the web interface at: **http://localhost:8000/static**

## 📁 Project Structure

```
dynabotbackend/
├── main.py                    # FastAPI application entry point
├── settings.json              # Configuration (API keys)
├── requirements.txt           # Python dependencies
├── frontend/                  # Web interface (HTML/CSS/JS)
│   ├── index.html            # Main chat interface
│   ├── login.html            # User login page
│   ├── register.html         # User registration page
│   └── *.css, *.js           # Styling and functionality
├── services/                 # Core business logic
│   ├── AnswerQuestions.py    # Query processing and AI responses
│   ├── DocumentProcessing.py # Document parsing
│   ├── VectoreStore.py       # Vector database management
│   ├── TextProcessing.py     # Text embedding and processing
│   └── Crawler.py            # Web content scraping
├── models/                   # Database models
│   ├── models.py             # SQLAlchemy models
│   └── schema.py             # Pydantic schemas
├── auth/                     # Authentication
│   └── auth.py               # User login/registration logic
├── database/                 # Database configuration
│   └── database.py           # Database connection and setup
└── env/                      # Python virtual environment
```

## 🔧 Main Commands

| Command | Purpose |
|---------|---------|
| `python run_ingest.py` | Process documents and create embeddings |
| `python run_embed_only.py` | Only create embeddings (lightweight) |
| `python run_ingest_standalone.py` | Standalone ingest without dependencies |
| `python main.py` | Start the FastAPI web server |

## 📚 How It Works

### User Journey

1. **User Creates Account** → Register on DynaBot platform
2. **Input Knowledge** → Upload documents, add website URLs, or type information
3. **System Processes Data** → Creates embeddings and indexes content
4. **Chatbot Generated** → Instantly ready for use
5. **Share Instantly** → Get unique URL and QR code to share
6. **End Users Chat** → Anyone with the link asks questions, gets answers

### Behind the Scenes

**Data Processing Pipeline:**
1. Extract content from files, websites, or text input
2. Parse and split into manageable chunks
3. Create embeddings using OpenAI
4. Store vectors in Pinecone for fast retrieval
5. Generate shareable chatbot interface

**Question Answering (End-User Side):**
1. Visitor asks question via shared chatbot
2. Query converted to embedding vector
3. Pinecone finds relevant document chunks
4. GPT-4o generates answer with context
5. Response returned to visitor

## 🔐 Authentication & Multi-Tenancy

- **User Accounts**: Sign up and create accounts on the platform
- **Isolated Data**: Each user's documents and chatbots are completely separate
- **Multiple Chatbots**: Users can create multiple chatbots from different data sources
- **Share Securely**: Public chatbots are accessible via URL/QR, private data stays protected

## 💾 Data Storage

- **User Accounts**: SQL database stores user profiles and chatbot metadata
- **Vector Database**: Pinecone stores embeddings, indexed by user and chatbot
- **Isolation**: Each user's data completely separate with namespace/index separation
- **API Keys**: Stored in `settings.json` (never commit to version control!)

## 🛠️ Troubleshooting

### API Keys Not Found
- Ensure `settings.json` has valid OpenAI and Pinecone keys
- Check that `settings.json` is in the project root directory

### Documents Not Processing
- Run `python run_ingest.py` to process documents
- Check database connection is working
- Verify Pinecone index is created for your user ID

### Server Won't Start
- Ensure port 8000 is not in use
- Check all dependencies are installed: `pip install -r requirements.txt`
- Verify Python 3.8+ is installed

## 📋 Requirements

Key dependencies include:
- **FastAPI** - Web framework
- **LangChain** - Document processing
- **Pinecone** - Vector database
- **OpenAI** - Language models and embeddings
- **SQLAlchemy** - Database ORM
- **BeautifulSoup** - Web scraping

See `requirements.txt` for complete list.

## 🚦 API Endpoints

- `POST /auth/register` - Create new user account
- `POST /auth/login` - Login user
- `POST /chatbot/create` - Create new chatbot from data
- `POST /chatbot/{chatbot_id}/upload` - Upload documents
- `POST /chatbot/{chatbot_id}/add-url` - Add website content
- `POST /chatbot/{chatbot_id}/add-text` - Add typed information
- `POST /chatbot/{chatbot_id}/chat` - Public endpoint for asking questions
- `GET /chatbot/{chatbot_id}/share` - Get shareable link & QR code

## 📝 Notes

- **Multi-Tenant Architecture**: Each user completely isolated - no data leakage
- **QR Code Generation**: Instant shareable QR codes for chatbots
- **No-Code Setup**: Users don't need technical knowledge to create chatbots
- **Three Data Input Methods**: Upload files, crawl websites, or paste text
- **Privacy First**: Keep `settings.json` private - never commit API keys
- **Cloud-Based Storage**: Vector embeddings stored in Pinecone (not locally)
- **Requires Internet**: Needs OpenAI API and Pinecone access for operation

---

**Status**: Ready to use | **Python**: 3.8+ | **Framework**: FastAPI
