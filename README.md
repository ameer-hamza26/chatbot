# RAG Chatbot for TKR Restaurant

A Retrieval-Augmented Generation (RAG) chatbot application built with FastAPI, OpenAI GPT models, and ChromaDB. This intelligent chatbot helps customers with questions about TKR Restaurant's menu, services, and general information.

## 🚀 Features

- **RAG-Powered Chat**: Uses vector database to retrieve relevant context from restaurant documentation
- **PDF Document Ingestion**: Upload and index PDF documents to build a knowledge base
- **Conversational History**: Maintains chat history using MongoDB for context-aware responses
- **Modern Web Interface**: Clean and responsive frontend built with vanilla HTML/CSS/JavaScript
- **RESTful API**: Well-documented FastAPI backend with Swagger UI
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Vector Search**: Semantic search using ChromaDB for finding relevant information

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **OpenAI GPT-4o-mini** - Language model for generating responses
- **ChromaDB** - Vector database for semantic search
- **MongoDB** - NoSQL database for chat history
- **LangChain** - Framework for building LLM applications
- **Sentence Transformers** - Embedding models for vector search
- **PyPDF** - PDF processing and text extraction

### Frontend
- **HTML5/CSS3/JavaScript** - Vanilla web technologies
- **Fetch API** - For API communication

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Uvicorn** - ASGI server

## 📋 Prerequisites

- **Python 3.11 or 3.12** (Python 3.13 is not supported yet due to PyTorch compatibility)
- **OpenAI API Key** - Get one from [OpenAI Platform](https://platform.openai.com/api-keys)
- **MongoDB** - Running locally or connection string for remote instance
- **Docker** (optional) - Only if using Docker deployment

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd chatbot
```

### 2. Create Virtual Environment

```bash
# Using Python 3.11
python3.11 -m venv venv

# Or using Python 3.12
python3.12 -m venv venv
```

### 3. Activate Virtual Environment

```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Environment Setup

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**Note**: Make sure MongoDB is running. The application will connect to MongoDB at `mongodb://localhost:27017` by default.

## 🚀 Running the Application

### Method 1: Quick Start (Using Script)

```bash
chmod +x run.sh
./run.sh
```

This script will:
- Check/create virtual environment
- Verify `.env` file exists
- Install dependencies
- Start the server

### Method 2: Manual Start

```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables auto-reload on code changes (useful for development).

### Method 3: Docker (Recommended for Production)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

## 📍 Access Points

Once the application is running, you can access:

- **Frontend**: http://localhost:8000
- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

### Chat Endpoints

- `POST /api/chat` - Send a message to the chatbot
  ```json
  {
    "message": "What menu items do you have?"
  }
  ```

- `POST /api/clear-chat` - Clear chat history

### Document Ingestion

- `POST /api/ingest` - Ingest a PDF document into the knowledge base
  ```json
  {
    "pdf_path": "./tkr.pdf"
  }
  ```

### Utility Endpoints

- `GET /` - Serve frontend interface
- `GET /health` - Health check endpoint

## 📁 Project Structure

```
chatbot/
├── main.py                 # FastAPI application entry point
├── chat_bot.py            # ChatBot class with OpenAI integration
├── vector_db.py           # Vector database handler (ChromaDB)
├── database.py            # MongoDB handler for chat history
├── pdf_handler.py          # PDF processing and text extraction
├── first_run.py           # Initial PDF ingestion script
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image configuration
├── docker-compose.yml     # Docker Compose configuration
├── run.sh                 # Quick start script
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore rules
├── .dockerignore         # Docker ignore rules
├── frontend/
│   ├── index.html        # Frontend interface
│   └── style.css         # Frontend styles
├── vector_db/            # ChromaDB data (auto-generated)
└── venv/                 # Virtual environment (not in git)
```

## 🔄 Initial Setup (First Run)

Before using the chatbot, you need to ingest PDF documents:

### Option 1: Using the API

```bash
curl -X POST "http://localhost:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{"pdf_path": "./tkr.pdf"}'
```

### Option 2: Using the Script

```bash
python first_run.py
```

This will process the PDF files listed in `first_run.py` and add them to the vector database.

## 🐳 Docker Commands

```bash
# Build and start
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Rebuild and restart
docker-compose up --build --force-recreate
```

## 🔍 How It Works

1. **Document Ingestion**: PDFs are processed, split into chunks, and embedded into ChromaDB
2. **User Query**: When a user sends a message, the system searches the vector database for relevant context
3. **Context Retrieval**: Top-k most relevant document chunks are retrieved based on semantic similarity
4. **Response Generation**: The retrieved context, along with chat history, is sent to OpenAI GPT model
5. **History Storage**: Both user messages and bot responses are stored in MongoDB for context

## 🛠️ Development

### Running in Development Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag automatically restarts the server when code changes are detected.

### Testing the API

You can test the API using:
- **Swagger UI**: http://localhost:8000/docs (Interactive API documentation)
- **cURL**: Command-line tool
- **Postman**: API testing tool
- **Frontend**: Built-in web interface at http://localhost:8000

## ⚠️ Troubleshooting

### PyTorch Installation Fails
**Solution**: Make sure you're using Python 3.11 or 3.12, not 3.13.

### OPENAI_API_KEY Not Found
**Solution**: Create a `.env` file in the project root with your OpenAI API key.

### Port 8000 Already in Use
**Solution**: 
- Change the port: `uvicorn main:app --port 8001`
- Or stop the process: `lsof -ti:8000 | xargs kill`

### MongoDB Connection Error
**Solution**: Make sure MongoDB is running:
```bash
# Check if MongoDB is running
mongosh  # or mongo (older versions)

# Start MongoDB (if not running)
# macOS with Homebrew:
brew services start mongodb-community

# Linux:
sudo systemctl start mongod
```

### Vector Database Errors
**Solution**: The `vector_db` directory will be created automatically. Make sure it has write permissions.

## 📝 Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Optional variables:
```env
OPENAI_API_KEY_BACKUP=backup_key_here  # Fallback API key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is part of a Computational Intelligence course project.

## 🙏 Acknowledgments

- OpenAI for GPT models
- LangChain for the LLM framework
- ChromaDB for vector database
- FastAPI for the web framework

---

**Note**: This is a development project. For production use, consider:
- Adding authentication/authorization
- Implementing rate limiting
- Using environment-specific configurations
- Setting up proper logging and monitoring
- Securing API endpoints

