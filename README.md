# U-Intelligence

**UBL Knowledge Assistant - Department-Specific Knowledge Management System**

U-Intelligence is a full-stack enterprise application designed to eliminate coordination friction across UBL's 17 departments by providing a centralized, intelligent system for accessing SOPs, policies, and procedures through an intuitive conversational interface.

## Quick Links

- 📖 **[Documentation](./docs/README.md)** - Complete documentation
- 🚀 **[Setup Guide](./docs/SETUP.md)** - Get started in 5 minutes
- 🌐 **[API Reference](./docs/API.md)** - API endpoints and examples
- 🚢 **[Deployment Guide](./docs/DEPLOYMENT.md)** - Production deployment
- 🔧 **[Troubleshooting](./docs/TROUBLESHOOTING.md)** - Common issues & solutions
- 🏗️ **[Architecture](./ARCHITECTURE.md)** - System design overview

## Features

- **17 Department Support**: Isolated knowledge bases for each UBL department
- **Conversational Chat Interface**: Natural language interaction with RAG integration
- **Conversation Memory**: User-controlled context management
- **File Upload**: Department-specific document management
- **Professional UI**: Corporate-grade design with smooth animations
- **Scalable Architecture**: Clean separation of concerns for easy deployment

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Gemini API key (get it from [makersuite.google.com](https://makersuite.google.com/app/apikey))

### Backend Setup (5 minutes)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
python run.py
```

Backend runs at: `http://localhost:8000`

### Frontend Setup (2 minutes)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:3001`

## Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── core/           # Configuration & database
│   │   ├── models/         # Database models
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic (RAG)
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   ├── run.py
│   └── .env.example        # Configuration template
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API client
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── docs/                   # Documentation
│   ├── SETUP.md
│   ├── DEPLOYMENT.md
│   ├── TROUBLESHOOTING.md
│   ├── API.md
│   └── README.md
└── ARCHITECTURE.md         # System architecture
```

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite
- **Vector DB**: Chroma
- **LLM**: Google Gemini
- **ORM**: SQLAlchemy

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **Styling**: CSS3

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/departments` | List all departments |
| POST | `/api/chat` | Send message |
| GET | `/api/chat/{id}/messages` | Get conversation |
| GET | `/api/conversations/{dept}` | List conversations |
| POST | `/api/upload/{dept}` | Upload document |

See [API.md](./docs/API.md) for complete reference.

## Configuration

### Environment Variables

Create `backend/.env` from `backend/.env.example`:

```env
GEMINI_API_KEY=your_api_key_here
RAG_ENABLED=True
DATABASE_URL=sqlite:///./u_intelligence.db
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

See [SETUP.md](./docs/SETUP.md) for all configuration options.

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

### Code Quality

```bash
# Backend linting
cd backend
flake8 app/

# Frontend linting
cd frontend
npm run lint
```

## Deployment

For production deployment, see [DEPLOYMENT.md](./docs/DEPLOYMENT.md).

Quick deployment with Docker:

```bash
docker-compose up -d
```

## Troubleshooting

Common issues and solutions are documented in [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md).

Quick health check:

```bash
curl http://localhost:8000/api/health
```

## Documentation

Complete documentation is available in the [docs/](./docs/) folder:

- **[SETUP.md](./docs/SETUP.md)** - Development environment setup
- **[DEPLOYMENT.md](./docs/DEPLOYMENT.md)** - Production deployment
- **[API.md](./docs/API.md)** - API reference
- **[TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)** - Common issues
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design

## Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)
2. Review relevant documentation
3. Check application logs
4. Contact the development team

## License

[Add your license information here]

## Version

Current version: **1.0.0**

## Contributing

Contributions are welcome! Please:
1. Follow existing code structure
2. Update documentation
3. Test thoroughly
4. Submit pull request with clear description

---

**Last Updated**: March 8, 2026

```cmd
# Setup backend
setup_backend.bat

# Setup frontend  
setup_frontend.bat

# Run backend (Terminal 1)
run_backend.bat

# Run frontend (Terminal 2)
run_frontend.bat
```

**Mac/Linux:**
```bash
# Make scripts executable
chmod +x setup_backend.sh setup_frontend.sh run_backend.sh run_frontend.sh

# Setup backend
./setup_backend.sh

# Setup frontend
./setup_frontend.sh

# Run backend (Terminal 1)
./run_backend.sh

# Run frontend (Terminal 2)
./run_frontend.sh
```

### Manual Setup

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (optional, defaults are provided):
```bash
cp .env.example .env
```

5. Run the backend server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (optional):
```bash
VITE_API_URL=http://localhost:8000/api
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

> **📖 For detailed setup instructions, see [SETUP.md](SETUP.md)**

## Usage

1. **Select Department**: On initial load, choose from 17 UBL departments
2. **Start Chat**: Ask questions about department-specific SOPs and policies
3. **Upload Documents**: Use the upload button to add new SOPs and policies
4. **Manage Conversations**: View, select, and delete previous conversations from the sidebar
5. **Toggle Memory**: Enable/disable conversation memory for context-aware responses

## API Endpoints

### Departments
- `GET /api/departments/` - Get all departments
- `GET /api/departments/{code}` - Get specific department

### Chat
- `POST /api/chat/` - Send a message
- `GET /api/chat/{conversation_id}/messages` - Get conversation messages

### Upload
- `POST /api/upload/{department_id}` - Upload a document
- `GET /api/upload/{department_id}/files` - List uploaded files

### Conversations
- `GET /api/conversations/{department_id}` - Get all conversations for a department
- `GET /api/conversations/detail/{conversation_id}` - Get conversation details
- `DELETE /api/conversations/{conversation_id}` - Delete a conversation
- `PATCH /api/conversations/{conversation_id}/memory` - Toggle memory

## RAG Integration

The application includes a RAG service abstraction layer (`app/services/rag_service.py`) that provides:

- **Document Ingestion**: `ingest_document()` - For ingesting uploaded documents
- **Query Processing**: `query()` - For generating responses based on department knowledge
- **Document Management**: `delete_document()` - For removing documents

The RAG service is currently a stub implementation. To integrate actual RAG functionality:

1. Update `RAG_ENABLED` in configuration
2. Implement document parsing (PDF, DOCX, TXT)
3. Implement embedding generation
4. Implement vector database storage
5. Implement LLM integration for response generation

See `backend/app/services/rag_service.py` for detailed integration points.

## Departments

The system supports 17 UBL departments:

1. Branch Banking
2. Audit and Risk Review
3. Compliance
4. CIBG (Corporate and Investment Banking Group)
5. Digital Banking Group
6. Finance
7. Human Resource Group
8. Information Technology
9. Islamic Banking
10. Legal and Secretary Dept
11. Operations and Transformation
12. Risk and Credit Policy
13. Shared Services Group
14. Special Assets Management
15. Treasury and Capital Markets
16. UBL International
17. Consumer Banking Group

## Database

The application uses SQLite by default (configurable via `DATABASE_URL`). Tables are automatically created on first run:

- `conversations` - Stores conversation metadata
- `messages` - Stores individual chat messages
- `departments` - Stores department information

## Deployment

### Backend Deployment

1. Set production environment variables
2. Use a production ASGI server (e.g., Gunicorn with Uvicorn workers)
3. Configure reverse proxy (Nginx)
4. Set up SSL certificates

Example Gunicorn command:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment

1. Build the production bundle:
```bash
npm run build
```

2. Serve the `dist` folder using a web server (Nginx, Apache, or CDN)

## Configuration

### Backend Configuration

Key configuration options in `backend/app/core/config.py`:

- `DATABASE_URL`: Database connection string
- `CORS_ORIGINS`: Allowed CORS origins
- `UPLOAD_DIR`: File upload directory
- `MAX_UPLOAD_SIZE`: Maximum file size (default: 50MB)
- `RAG_ENABLED`: Enable/disable RAG functionality
- `DEPARTMENTS_STORAGE_BASE`: Base directory for department-specific storage

### Frontend Configuration

- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000/api`)

## Security Considerations

- Implement authentication/authorization for production
- Validate and sanitize file uploads
- Implement rate limiting
- Use HTTPS in production
- Secure database credentials
- Implement proper logging and monitoring

## Future Enhancements

- User authentication and authorization
- Advanced search capabilities
- Document versioning
- Analytics and reporting
- Multi-language support
- Mobile application
- Integration with existing UBL systems

## License

Proprietary - UBL Internal Use Only

## Support

For issues and questions, contact the development team.

