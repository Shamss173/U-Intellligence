# Troubleshooting Guide

## Common Issues & Solutions

### Backend Issues

#### 1. Port 8000 Already in Use

**Error**: `[Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)`

**Solution**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

#### 2. GEMINI_API_KEY Not Found

**Error**: `GEMINI_API_KEY is empty!`

**Solution**:
1. Check `.env` file exists in `backend/` directory
2. Verify `GEMINI_API_KEY=<your_key>` is set
3. Restart backend: `python run.py`

#### 3. RAG Service Not Initializing

**Error**: `RAG disabled` in logs

**Causes & Solutions**:
- Chroma not installed: `pip install chromadb`
- Google Generative AI not installed: `pip install google-generativeai`
- Vector database not found: Check `./my_vector_db_v2` exists
- API key invalid: Verify key in `.env`

#### 4. Database Locked Error

**Error**: `database is locked`

**Solution**:
```bash
# Remove database file
rm backend/u_intelligence.db

# Restart backend - it will recreate the database
python run.py
```

#### 5. Import Errors

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
# Ensure you're in the backend directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt

# Run from backend directory
python run.py
```

### Frontend Issues

#### 1. Port 3000/3001 Already in Use

**Error**: `Port 3000 is in use, trying another one...`

**Solution**: This is normal - Vite will use the next available port (usually 3001)

#### 2. API Connection Failed

**Error**: `Cannot GET /api/health` or CORS errors

**Causes & Solutions**:
- Backend not running: Start backend with `python run.py`
- Wrong API URL: Check `frontend/src/services/api.js`
- CORS not configured: Verify `CORS_ORIGINS` in `backend/.env`

#### 3. Blank Page or 404

**Error**: Frontend loads but shows blank page

**Solution**:
1. Check browser console for errors (F12)
2. Verify backend is running: `curl http://localhost:8000/api/health`
3. Clear browser cache: Ctrl+Shift+Delete
4. Restart frontend: `npm run dev`

#### 4. Dependencies Not Installed

**Error**: `npm ERR! code ERESOLVE`

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### RAG System Issues

#### 1. "Knowledge Base Not Available"

**Cause**: Vector database collection not found

**Solution**:
```bash
# Check if vector database exists
ls -la my_vector_db_v2/

# If missing, you need to re-embed documents
# Contact system administrator
```

#### 2. Embedding Dimension Mismatch

**Error**: `dimension mismatch` in logs

**Cause**: Old embeddings (1024D) vs new model (3072D)

**Solution**: This is handled automatically with fallback to simple retrieval. No action needed.

#### 3. No Response from RAG

**Error**: Query returns empty or generic response

**Causes & Solutions**:
- Vector database empty: Re-embed documents
- Query too specific: Try broader queries
- API rate limited: Wait a moment and retry
- Gemini API down: Check https://status.cloud.google.com/

#### 4. Slow Response Times

**Cause**: Large number of embeddings or network latency

**Solution**:
- Reduce `RAG_TOP_K` in `.env` (default: 5)
- Optimize Gemini API calls
- Check network connectivity
- Consider caching responses

### Database Issues

#### 1. Conversation Not Saving

**Error**: Messages disappear after refresh

**Cause**: Database not persisting

**Solution**:
```bash
# Check database file exists
ls -la backend/u_intelligence.db

# Check database permissions
chmod 644 backend/u_intelligence.db

# Restart backend
python run.py
```

#### 2. Duplicate Conversations

**Cause**: Multiple backend instances running

**Solution**:
```bash
# Kill all Python processes
pkill -f "python run.py"

# Start single backend instance
python run.py
```

### Performance Issues

#### 1. Slow Chat Response

**Causes**:
- Large context window (many previous messages)
- Slow network connection
- Gemini API rate limiting

**Solutions**:
- Disable memory for faster responses
- Reduce `RAG_TOP_K` value
- Check network speed
- Wait before retrying if rate limited

#### 2. High Memory Usage

**Cause**: Large vector database or many conversations

**Solution**:
- Archive old conversations
- Reduce `RAG_TOP_K` value
- Restart backend periodically

### Logging & Debugging

#### Enable Debug Logging

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or modify backend/app/main.py
logging.basicConfig(level=logging.DEBUG)
```

#### View Logs

```bash
# Backend logs
tail -f backend/app.log

# Frontend console
# Open browser DevTools: F12 → Console tab
```

#### Check RAG Service Status

```bash
curl http://localhost:8000/api/health | python -m json.tool
```

Expected output:
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

## Getting Help

1. **Check Logs**: Always check logs first for error messages
2. **Verify Configuration**: Ensure `.env` is properly configured
3. **Test Components**: Test backend and frontend separately
4. **Check Dependencies**: Verify all packages are installed
5. **Review Documentation**: Check SETUP.md and API documentation

## Reporting Issues

When reporting issues, include:
1. Error message (full stack trace)
2. Steps to reproduce
3. Environment (OS, Python version, Node version)
4. Relevant logs
5. Configuration (without sensitive data)
