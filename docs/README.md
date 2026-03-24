# U-Intelligence Documentation

Welcome to the U-Intelligence documentation. This folder contains comprehensive guides for setting up, deploying, and troubleshooting the system.

## Quick Navigation

### Getting Started
- **[SETUP.md](./SETUP.md)** - Development environment setup and local development
- **[API.md](./API.md)** - Complete API reference and examples

### Operations
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production deployment guide
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and solutions

### Architecture
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - System design and architecture overview

## Documentation Structure

```
docs/
├── README.md                 # This file
├── SETUP.md                  # Development setup guide
├── DEPLOYMENT.md             # Production deployment
├── TROUBLESHOOTING.md        # Common issues & solutions
└── API.md                    # API reference
```

## For Different Roles

### Developers
1. Start with [SETUP.md](./SETUP.md) to set up your development environment
2. Read [API.md](./API.md) to understand the API
3. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) when you encounter issues

### DevOps/System Administrators
1. Read [DEPLOYMENT.md](./DEPLOYMENT.md) for production setup
2. Review [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for monitoring and maintenance
3. Check [API.md](./API.md) for health check endpoints

### Product Managers/Business Users
1. Check [ARCHITECTURE.md](../ARCHITECTURE.md) for system overview
2. Review [API.md](./API.md) for available features
3. Refer to [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common questions

## Key Features

- **17 Department Support**: Isolated knowledge bases for each department
- **Conversational Interface**: Natural language chat with RAG integration
- **Memory Management**: User-controlled conversation memory
- **File Upload**: Department-specific document management
- **Professional UI**: Corporate-grade design with smooth interactions

## System Requirements

### Minimum
- Python 3.8+
- Node.js 16+
- 2GB RAM
- 500MB disk space

### Recommended
- Python 3.11+
- Node.js 18+
- 4GB RAM
- 2GB disk space (for vector database)

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your Gemini API key
python run.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Access the application at `http://localhost:3001`

## API Documentation

Interactive API documentation is available at `http://localhost:8000/docs` when the backend is running.

## Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. Review relevant documentation section
3. Check application logs for error messages
4. Contact the development team

## Contributing

When contributing to the project:
1. Follow the existing code structure
2. Update relevant documentation
3. Test changes thoroughly
4. Submit pull request with clear description

## Version History

- **v1.0.0** (Current) - Initial release with RAG integration

## License

[Add your license information here]

## Contact

For questions or support, contact: [Add contact information]
