# Development Environment Setup

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Git

## Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get it from: https://makersuite.google.com/app/apikey
```

### 4. Initialize Database

The database is created automatically on first run. No manual initialization needed.

### 5. Run Backend

```bash
python run.py
```

Backend will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

Frontend will be available at: `http://localhost:3001` (or next available port)

## Verification

### Backend Health Check

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "U-Intelligence API",
  "version": "1.0.0",
  "rag_enabled": true,
  "rag_client": true,
  "rag_gemini": true
}
```

### Frontend Access

Open browser and navigate to: `http://localhost:3001`

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Missing Dependencies

If you get import errors:
```bash
# Reinstall all dependencies
pip install --upgrade -r requirements.txt
```

### Database Issues

If you encounter database errors:
```bash
# Remove the database file (data will be lost)
rm u_intelligence.db

# Restart the backend - it will recreate the database
python run.py
```

### RAG Service Not Working

Check the logs for:
1. GEMINI_API_KEY is set in .env
2. Vector database exists at `./my_vector_db_v2`
3. Chroma is properly installed: `pip install chromadb`

## Environment Variables

See `backend/.env.example` for all available configuration options.

Key variables:
- `GEMINI_API_KEY`: Required for RAG functionality
- `RAG_ENABLED`: Set to `True` to enable RAG
- `DATABASE_URL`: SQLite database location
- `CORS_ORIGINS`: Allowed frontend origins
