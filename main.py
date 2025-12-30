from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import sys
import warnings
import logging

# Suppress TensorFlow and protobuf warnings/errors before importing modules
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# Fix HuggingFace tokenizers parallelism warning
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
warnings.filterwarnings('ignore')
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# Filter stderr to suppress protobuf AttributeError messages
class FilterStderr:
    def __init__(self):
        self.stderr = sys.stderr
    
    def write(self, text):
        # Filter out protobuf AttributeError messages
        if 'AttributeError' in text and 'GetPrototype' in text:
            return  # Suppress this specific error
        self.stderr.write(text)
    
    def flush(self):
        self.stderr.flush()

# Apply filter before importing modules that use TensorFlow
sys.stderr = FilterStderr()

from chat_bot import ChatBot
from vector_db import VectorDatabase
from pdf_handler import PDFHandler
from database import DatabaseHandler

# Hardcoded User ID
USER_ID = "restaurant_user_001"

# Initialize FastAPI app
app = FastAPI(title="RAG Chatbot API", version="1.0.0")

# Ingestion endpoint
class IngestRequest(BaseModel):
    pdf_path: str

@app.post("/api/ingest")
async def ingest_document(request: IngestRequest):
    try:
        if vector_db is None:
            raise HTTPException(status_code=503, detail="Vector database is not available.")
        
        pdf_path = request.pdf_path
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail=f"File not found: {pdf_path}")
        
        file_name = os.path.basename(pdf_path)
        
        # Check if already present
        if vector_db.is_document_present(file_name):
            return {"message": f"Document '{file_name}' is already present in the RAG system. Skipping extraction and embedding.", "status": "skipped"}
        
        # Start extraction and embedding
        print(f"Extraction and embedding step started for: {file_name}")
        
        handler = PDFHandler(document_path=pdf_path)
        documents = handler.load_and_split()
        
        vector_db.add_documents(documents=documents)
        
        return {"message": f"Successfully indexed '{file_name}'", "status": "success"}
    
    except Exception as e:
        print(f"Error during ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot, vector database and database
try:
    db_handler = DatabaseHandler()
    print("DatabaseHandler initialized successfully")
except Exception as e:
    print(f"Error initializing DatabaseHandler: {e}")
    db_handler = None

try:
    restaurant_bot = ChatBot()
    print("ChatBot initialized successfully")
except Exception as e:
    print(f"Error initializing ChatBot: {e}")
    restaurant_bot = None

try:
    vector_db = VectorDatabase()
    print("VectorDatabase initialized successfully")
except Exception as e:
    print(f"Error initializing VectorDatabase: {e}")
    vector_db = None

# Mount static files for frontend (CSS, JS, etc.)
try:
    if os.path.exists("frontend"):
        app.mount("/static", StaticFiles(directory="frontend"), name="static")
except Exception as e:
    print(f"Warning: Could not mount static files: {e}")

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Serve frontend at root
@app.get("/")
async def serve_frontend():
    try:
        if os.path.exists("frontend/index.html"):
            return FileResponse("frontend/index.html")
        else:
            return {"message": "RAG Chatbot API is running", "status": "healthy", "note": "Frontend not found"}
    except Exception as e:
        return {"message": "RAG Chatbot API is running", "status": "healthy", "error": str(e)}

# Chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Check if services are initialized
        if restaurant_bot is None:
            raise HTTPException(status_code=503, detail="ChatBot service is not available. Please check the configuration.")
        
        if vector_db is None:
            raise HTTPException(status_code=503, detail="Vector database is not available. Please check the configuration.")
        
        if db_handler is None:
            raise HTTPException(status_code=503, detail="Database service is not available.")
        
        user_prompt = request.message.strip()
        
        if not user_prompt:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get last 10 messages for context (before adding current one)
        history = await db_handler.get_recent_history(USER_ID, limit=10)
        
        # Save current user message to DB
        await db_handler.save_message(USER_ID, user_prompt, "user")
        
        # Search in vector db to get context related to user prompt
        try:
            context_docs = vector_db.search(query_text=user_prompt, docs_to_search=8)
        except Exception as e:
            print(f"Error searching vector database: {e}")
            context_docs = []
        
        # Format context from documents
        if context_docs and len(context_docs) > 0:
            # Format context with better structure
            context_parts = []
            for i, doc in enumerate(context_docs, 1):
                content = doc.page_content.strip()
                if content:
                    context_parts.append(f"[Context {i}]\n{content}")
            context = "\n\n".join(context_parts)
        else:
            # No context found - still allow the model to respond but inform it
            context = "No specific context found in the knowledge base for this query."
        
        # Generate response from chatbot with history
        response = restaurant_bot.generate_response(context=context, user_prompt=user_prompt, history=history)
        
        # Save bot response to DB
        await db_handler.save_message(USER_ID, response, "bot")
        
        return ChatResponse(response=response)
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"Error in chat endpoint: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {error_msg}")

@app.post("/api/clear-chat")
async def clear_chat():
    try:
        if db_handler:
            await db_handler.clear_history(USER_ID)
            return {"message": "Chat history cleared", "status": "success"}
        raise HTTPException(status_code=503, detail="Database not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health():
    return {"message": "RAG Chatbot API is running", "status": "healthy"}
