# How to Run the Backend

This guide explains how to run the RAG Chatbot backend both directly and using Docker.

## Prerequisites

1. **Python 3.11 or 3.12** (required for PyTorch support)
   - Python 3.13 is not supported yet due to PyTorch compatibility
2. **OpenAI API Key** - Get one from https://platform.openai.com/api-keys
3. **Docker** (optional, only if using Docker)

## Environment Setup

1. Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Method 1: Run Directly (Without Docker)

### Step 1: Create Virtual Environment (if not already created)

```bash
# If using Python 3.11
python3.11 -m venv venv

# Or if using Python 3.12
python3.12 -m venv venv
```

### Step 2: Activate Virtual Environment

```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Run the Backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables auto-reload on code changes (useful for development).

### Step 5: Access the Application

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Frontend**: http://localhost:8000 (serves the frontend/index.html)

## Method 2: Run with Docker

### Option A: Using Docker Compose (Recommended)

1. **Build and run:**
```bash
docker-compose up --build
```

2. **Run in detached mode (background):**
```bash
docker-compose up -d --build
```

3. **View logs:**
```bash
docker-compose logs -f
```

4. **Stop the container:**
```bash
docker-compose down
```

### Option B: Using Docker Commands Directly

1. **Build the Docker image:**
```bash
docker build -t rag-chatbot-backend .
```

2. **Run the container:**
```bash
docker run -d \
  --name rag-chatbot-backend \
  -p 8000:8000 \
  -v $(pwd)/vector_db:/app/vector_db \
  -v $(pwd)/.env:/app/.env \
  rag-chatbot-backend
```

3. **View logs:**
```bash
docker logs -f rag-chatbot-backend
```

4. **Stop the container:**
```bash
docker stop rag-chatbot-backend
docker rm rag-chatbot-backend
```

## Useful Commands

### Docker Commands
```bash
# List running containers
docker ps

# List all containers
docker ps -a

# View container logs
docker logs rag-chatbot-backend

# Access container shell
docker exec -it rag-chatbot-backend bash

# Remove container
docker rm rag-chatbot-backend

# Remove image
docker rmi rag-chatbot-backend
```

### Docker Compose Commands
```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and restart
docker-compose up --build
```

## Troubleshooting

### Issue: PyTorch installation fails
**Solution**: Make sure you're using Python 3.11 or 3.12, not 3.13.

### Issue: OPENAI_API_KEY not found
**Solution**: Create a `.env` file in the project root with your OpenAI API key.

### Issue: Port 8000 already in use
**Solution**: 
- Change the port in the command: `uvicorn main:app --port 8001`
- Or stop the process using port 8000: `lsof -ti:8000 | xargs kill`

### Issue: Vector database errors
**Solution**: The `vector_db` directory will be created automatically. Make sure it has write permissions.

### Issue: Docker build fails
**Solution**: 
- Make sure Docker is running
- Check that you have enough disk space
- Try: `docker system prune` to clean up

## Development vs Production

### Development (Direct Run)
- Use `--reload` flag for auto-reload
- Better for debugging
- Faster iteration

### Production (Docker)
- Consistent environment
- Easy deployment
- Isolated dependencies

## API Endpoints

- `GET /` - Serve frontend
- `GET /health` - Health check
- `POST /api/chat` - Chat with the bot
- `POST /api/ingest` - Ingest PDF documents
- `POST /api/clear-chat` - Clear chat history
- `GET /docs` - Interactive API documentation (Swagger UI)



