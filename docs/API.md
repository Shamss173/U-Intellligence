# API Reference

## Overview

U-Intelligence API is a RESTful API built with FastAPI. Interactive API documentation is available at `/docs` endpoint.

**Base URL**: `http://localhost:8000/api`

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Response Format

All responses are in JSON format.

### Success Response

```json
{
  "status": "success",
  "data": { /* response data */ }
}
```

### Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Endpoints

### Health Check

Check if the API and RAG service are running.

**Endpoint**: `GET /health`

**Response**:
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

---

### Departments

#### Get All Departments

**Endpoint**: `GET /departments`

**Response**:
```json
[
  {
    "id": 1,
    "code": "branch_banking",
    "name": "Branch Banking",
    "description": "Branch Banking operations and procedures"
  },
  {
    "id": 2,
    "code": "audit_risk",
    "name": "Audit and Risk Review",
    "description": "Audit and risk management procedures"
  }
]
```

#### Get Department by Code

**Endpoint**: `GET /departments/{code}`

**Parameters**:
- `code` (string): Department code (e.g., "branch_banking")

**Response**:
```json
{
  "id": 1,
  "code": "branch_banking",
  "name": "Branch Banking",
  "description": "Branch Banking operations and procedures"
}
```

---

### Chat

#### Send Message

Send a message to the RAG system and get a response.

**Endpoint**: `POST /chat`

**Request Body**:
```json
{
  "department_id": "branch_banking",
  "message": "What are the branch banking procedures?",
  "conversation_id": null,
  "memory_enabled": true
}
```

**Parameters**:
- `department_id` (string, required): Department code
- `message` (string, required): User message
- `conversation_id` (integer, optional): Existing conversation ID
- `memory_enabled` (boolean, optional): Enable conversation memory (default: true)

**Response**:
```json
{
  "conversation_id": 1,
  "message": "Branch banking procedures include...",
  "timestamp": "2026-03-08T09:21:56"
}
```

#### Get Conversation Messages

**Endpoint**: `GET /chat/{conversation_id}/messages`

**Parameters**:
- `conversation_id` (integer): Conversation ID

**Response**:
```json
[
  {
    "role": "user",
    "content": "What are the branch banking procedures?",
    "timestamp": "2026-03-08T09:21:00"
  },
  {
    "role": "assistant",
    "content": "Branch banking procedures include...",
    "timestamp": "2026-03-08T09:21:56"
  }
]
```

---

### Conversations

#### Get Conversations

**Endpoint**: `GET /conversations/{department_id}`

**Parameters**:
- `department_id` (string): Department code

**Response**:
```json
[
  {
    "id": 1,
    "department_id": "branch_banking",
    "title": "Branch Banking Procedures",
    "created_at": "2026-03-08T09:00:00",
    "updated_at": "2026-03-08T09:21:56",
    "memory_enabled": true
  }
]
```

#### Get Conversation Detail

**Endpoint**: `GET /conversations/detail/{conversation_id}`

**Parameters**:
- `conversation_id` (integer): Conversation ID

**Response**:
```json
{
  "id": 1,
  "department_id": "branch_banking",
  "title": "Branch Banking Procedures",
  "created_at": "2026-03-08T09:00:00",
  "updated_at": "2026-03-08T09:21:56",
  "memory_enabled": true,
  "message_count": 4
}
```

#### Delete Conversation

**Endpoint**: `DELETE /conversations/{conversation_id}`

**Parameters**:
- `conversation_id` (integer): Conversation ID

**Response**:
```json
{
  "message": "Conversation deleted successfully"
}
```

#### Toggle Memory

**Endpoint**: `PATCH /conversations/{conversation_id}/memory`

**Parameters**:
- `conversation_id` (integer): Conversation ID
- `memory_enabled` (boolean, query): Enable or disable memory

**Response**:
```json
{
  "id": 1,
  "memory_enabled": false
}
```

---

### File Upload

#### Upload File

Upload a document for a department.

**Endpoint**: `POST /upload/{department_id}`

**Parameters**:
- `department_id` (string): Department code
- `file` (file, required): Document file (PDF, DOCX, TXT)

**Response**:
```json
{
  "filename": "document.pdf",
  "size": 1024000,
  "uploaded_at": "2026-03-08T09:21:56",
  "status": "uploaded"
}
```

#### List Files

**Endpoint**: `GET /upload/{department_id}/files`

**Parameters**:
- `department_id` (string): Department code

**Response**:
```json
[
  {
    "filename": "document.pdf",
    "size": 1024000,
    "uploaded_at": "2026-03-08T09:21:56"
  }
]
```

#### Delete File

**Endpoint**: `DELETE /upload/{department_id}/files/{filename}`

**Parameters**:
- `department_id` (string): Department code
- `filename` (string): File name

**Response**:
```json
{
  "message": "File deleted successfully"
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

## Rate Limiting

Currently, there is no rate limiting. This may be added in future versions.

## Pagination

Pagination is not currently implemented. All results are returned in full.

## Versioning

Current API version: `1.0.0`

API versioning may be added in future versions using URL prefixes (e.g., `/api/v2/`).

## Examples

### Example 1: Send a Chat Message

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "department_id": "branch_banking",
    "message": "What is UBL Debit Card?",
    "memory_enabled": true
  }'
```

### Example 2: Get Departments

```bash
curl http://localhost:8000/api/departments
```

### Example 3: Get Conversation Messages

```bash
curl http://localhost:8000/api/chat/1/messages
```

### Example 4: Upload a File

```bash
curl -X POST http://localhost:8000/api/upload/branch_banking \
  -F "file=@document.pdf"
```

## Interactive Documentation

For interactive API documentation with try-it-out functionality:

1. Start the backend: `python run.py`
2. Open browser: `http://localhost:8000/docs`
3. Explore and test endpoints directly in the browser

## SDK/Client Libraries

Currently, no official SDKs are available. Use the REST API directly or create a client using your preferred HTTP library.

### JavaScript/TypeScript Example

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// Send message
const response = await api.post('/chat', {
  department_id: 'branch_banking',
  message: 'What is UBL Debit Card?',
  memory_enabled: true
})

console.log(response.data)
```

### Python Example

```python
import requests

api_url = 'http://localhost:8000/api'

# Send message
response = requests.post(f'{api_url}/chat', json={
    'department_id': 'branch_banking',
    'message': 'What is UBL Debit Card?',
    'memory_enabled': True
})

print(response.json())
```
