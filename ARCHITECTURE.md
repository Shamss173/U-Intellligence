# U-Intelligence Architecture

## System Overview

U-Intelligence is a full-stack enterprise application built with React (frontend) and FastAPI (backend), designed to provide department-specific knowledge assistance through a conversational interface.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Department  │  │     Chat     │  │   Sidebar    │      │
│  │  Selection   │  │  Interface   │  │  (History)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Service Layer (Axios)                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Departments  │  │     Chat     │  │  Upload      │      │
│  │   Router     │  │    Router    │  │   Router     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Conversations │  │   Database   │  │ RAG Service  │      │
│  │   Router     │  │   (SQLite)   │  │ (Abstracted) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                             │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  Database    │  │  File System │                        │
│  │  (SQLite)    │  │  (Uploads)   │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Backend Architecture

### Directory Structure

```
backend/
├── app/
│   ├── core/              # Core configuration
│   │   ├── config.py      # Application settings
│   │   └── database.py    # Database connection
│   ├── models/            # SQLAlchemy models
│   │   ├── conversation.py
│   │   └── department.py
│   ├── routers/           # API endpoints
│   │   ├── departments.py
│   │   ├── chat.py
│   │   ├── upload.py
│   │   └── conversations.py
│   ├── services/          # Business logic
│   │   ├── rag_service.py      # RAG abstraction
│   │   └── title_generator.py  # Title generation
│   └── main.py            # FastAPI application
├── requirements.txt
└── run.py
```

### Key Components

#### 1. Core Layer (`app/core/`)
- **config.py**: Centralized configuration management
  - Database settings
  - CORS configuration
  - File upload settings
  - RAG configuration (for future integration)
  
- **database.py**: Database connection and session management
  - SQLAlchemy engine
  - Session factory
  - Database dependency injection

#### 2. Models Layer (`app/models/`)
- **Conversation**: Stores conversation metadata
  - Department association
  - Memory toggle state
  - Timestamps
  - Auto-generated titles
  
- **Message**: Stores individual chat messages
  - Role (user/assistant)
  - Content
  - Timestamps
  - Conversation association

- **Department**: Department information
  - Code and name
  - Description
  - Metadata

#### 3. Routers Layer (`app/routers/`)
- **departments.py**: Department management
  - List all departments
  - Get department details
  
- **chat.py**: Chat functionality
  - Send messages
  - Retrieve conversation messages
  - RAG integration
  
- **upload.py**: File upload handling
  - Department-specific uploads
  - File validation
  - RAG ingestion trigger
  
- **conversations.py**: Conversation management
  - List conversations
  - Get conversation details
  - Delete conversations
  - Toggle memory

#### 4. Services Layer (`app/services/`)
- **rag_service.py**: RAG abstraction layer
  - `ingest_document()`: Document ingestion interface
  - `query()`: Query processing interface
  - `delete_document()`: Document deletion interface
  - Currently a stub implementation for future AI team integration
  
- **title_generator.py**: Conversation title generation
  - Generates titles from user prompts
  - Handles truncation and formatting

### Data Flow

1. **User sends message**:
   - Frontend → API → Chat Router
   - Chat Router → RAG Service (if enabled)
   - RAG Service → Vector DB (future)
   - Response → Database → Frontend

2. **File upload**:
   - Frontend → Upload Router
   - File validation → File system storage
   - RAG Service → Document ingestion
   - Metadata → Database

3. **Conversation retrieval**:
   - Frontend → Conversations Router
   - Database query → Message retrieval
   - Response → Frontend

## Frontend Architecture

### Directory Structure

```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── DepartmentSelection.jsx
│   │   ├── DepartmentSelection.css
│   │   ├── ChatInterface.jsx
│   │   └── ChatInterface.css
│   ├── services/          # API integration
│   │   └── api.js
│   ├── App.jsx            # Main app component
│   ├── App.css
│   ├── main.jsx           # Entry point
│   └── index.css          # Global styles
├── package.json
└── vite.config.js
```

### Key Components

#### 1. DepartmentSelection
- **Purpose**: Initial department selection interface
- **Features**:
  - Grid layout of 17 departments
  - Search functionality
  - Smooth animations
  - Responsive design

#### 2. ChatInterface
- **Purpose**: Main chat interface for department-specific queries
- **Features**:
  - Message display
  - Input handling
  - Sidebar with conversation history
  - File upload
  - Memory toggle
  - Auto-scrolling
  - Timestamp display

#### 3. API Service Layer
- **Purpose**: Centralized API communication
- **Functions**:
  - Department operations
  - Chat operations
  - File upload
  - Conversation management

### State Management

- **Local State**: React hooks (useState, useEffect)
- **Routing**: React Router for navigation
- **API Calls**: Axios for HTTP requests
- **No Global State**: Simple component-level state management

## Database Schema

### Conversations Table
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    department_id TEXT NOT NULL,
    title TEXT,
    user_id TEXT,
    memory_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

### Departments Table
```sql
CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

## RAG Integration Points

The RAG service is abstracted to allow future AI team integration:

### 1. Document Ingestion
```python
async def ingest_document(
    department_id: str,
    file_path: str,
    metadata: Dict
) -> bool
```
**Integration Points**:
- Document parsing (PDF, DOCX, TXT)
- Text chunking
- Embedding generation
- Vector database storage
- Metadata indexing

### 2. Query Processing
```python
async def query(
    department_id: str,
    query: str,
    context: Optional[List[Dict]] = None
) -> str
```
**Integration Points**:
- Query embedding
- Vector similarity search
- Context retrieval
- LLM response generation
- Conversation context integration

### 3. Document Management
```python
async def delete_document(
    department_id: str,
    document_id: str
) -> bool
```
**Integration Points**:
- Vector database deletion
- Metadata cleanup
- Index updates

## Security Considerations

1. **Input Validation**: All user inputs validated
2. **File Upload Security**: File type and size validation
3. **CORS Configuration**: Restricted origins
4. **SQL Injection Prevention**: SQLAlchemy ORM
5. **Error Handling**: Comprehensive error handling and logging

## Scalability

### Current Architecture
- SQLite database (suitable for development/small deployments)
- File-based storage
- Single-server deployment

### Production Considerations
1. **Database**: Migrate to PostgreSQL or MySQL
2. **File Storage**: Use object storage (S3, Azure Blob)
3. **Caching**: Implement Redis for frequently accessed data
4. **Load Balancing**: Multiple backend instances
5. **CDN**: Static asset delivery
6. **Monitoring**: Application performance monitoring
7. **Logging**: Centralized logging system

## Deployment Architecture

### Development
```
Frontend (Vite Dev Server) → Backend (Uvicorn) → SQLite
```

### Production
```
CDN/Web Server → Frontend (Static) → Load Balancer → Backend (Gunicorn+Uvicorn) → PostgreSQL → Object Storage
```

## Future Enhancements

1. **Authentication**: User authentication and authorization
2. **Multi-tenancy**: Support for multiple organizations
3. **Advanced RAG**: Semantic search, hybrid search
4. **Analytics**: Usage analytics and reporting
5. **Real-time**: WebSocket support for real-time updates
6. **Mobile**: React Native mobile application
7. **Integration**: API for external system integration

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **File Handling**: aiofiles
- **Validation**: Pydantic

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Routing**: React Router
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Date Handling**: date-fns

### Development Tools
- **Backend**: Python 3.8+, pip
- **Frontend**: Node.js 16+, npm
- **Version Control**: Git

