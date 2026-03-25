"""
Run script for U-Intelligence backend
"""
import os
import sys
from pathlib import Path

# Ensure imports work from both `backend/app` and repo-root `rag_system/`.
backend_dir = Path(__file__).parent.resolve()
repo_root = backend_dir.parent.resolve()
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(repo_root))

# Run from backend directory so `import app...` works reliably.
os.chdir(backend_dir)
print(f"Changed working directory to: {os.getcwd()}")

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disabled auto-reload to prevent multiple RAG service instances
        log_level="info"
    )

