# Production Deployment Guide

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured for production
- [ ] Database backed up
- [ ] Vector database backed up
- [ ] API keys secured (not in version control)
- [ ] CORS origins updated for production domain
- [ ] Frontend build optimized

## Backend Deployment

### 1. Environment Configuration

Create production `.env` file:

```bash
# Use production values
GEMINI_API_KEY=<production_key>
DATABASE_URL=sqlite:///./data/u_intelligence.db
RAG_ENABLED=True
CORS_ORIGINS=["https://yourdomain.com"]
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Migration

```bash
# Ensure database directory exists
mkdir -p data

# Database will be created automatically on first run
```

### 4. Run with Production Server

```bash
# Using Gunicorn (recommended for production)
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

Or using Uvicorn with multiple workers:

```bash
pip install uvicorn

uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Enable HTTPS

Use a reverse proxy like Nginx:

```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Frontend Deployment

### 1. Build for Production

```bash
cd frontend
npm run build
```

This creates an optimized build in `dist/` directory.

### 2. Deploy Static Files

Upload the `dist/` directory to your web server or CDN.

### 3. Configure API Endpoint

Update `frontend/src/services/api.js` or use environment variable:

```bash
VITE_API_URL=https://api.yourdomain.com/api
```

### 4. Nginx Configuration

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    root /var/www/u-intelligence/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://api.yourdomain.com;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Docker Deployment (Optional)

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app.main:app"]
```

### Frontend Dockerfile

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY frontend/package*.json .
RUN npm ci

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DATABASE_URL=sqlite:///./data/u_intelligence.db
      - RAG_ENABLED=True
    volumes:
      - ./backend/data:/app/data
      - ./backend/my_vector_db_v2:/app/my_vector_db_v2

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
```

## Monitoring & Logging

### Application Logs

```bash
# View logs
tail -f /var/log/u-intelligence/app.log

# Rotate logs
logrotate /etc/logrotate.d/u-intelligence
```

### Health Checks

```bash
# Monitor backend health
curl https://api.yourdomain.com/api/health

# Set up monitoring alerts for non-200 responses
```

## Backup Strategy

### Database Backup

```bash
# Daily backup
0 2 * * * cp /app/data/u_intelligence.db /backups/u_intelligence_$(date +\%Y\%m\%d).db
```

### Vector Database Backup

```bash
# Weekly backup
0 3 * * 0 tar -czf /backups/vector_db_$(date +\%Y\%m\%d).tar.gz /app/my_vector_db_v2
```

## Performance Optimization

1. **Enable Caching**: Configure Redis for session caching
2. **CDN**: Serve static assets from CDN
3. **Database Indexing**: Ensure database indexes are created
4. **API Rate Limiting**: Implement rate limiting for API endpoints
5. **Compression**: Enable gzip compression in Nginx

## Security Considerations

1. **API Keys**: Use environment variables, never commit to version control
2. **HTTPS**: Always use HTTPS in production
3. **CORS**: Restrict CORS origins to your domain
4. **Input Validation**: All inputs are validated on backend
5. **SQL Injection**: Using SQLAlchemy ORM prevents SQL injection
6. **CSRF Protection**: Implement CSRF tokens if needed
7. **Rate Limiting**: Implement rate limiting to prevent abuse

## Rollback Procedure

```bash
# Keep previous version available
cp -r /app /app.backup

# If deployment fails, restore previous version
rm -rf /app
mv /app.backup /app

# Restart services
systemctl restart u-intelligence
```
