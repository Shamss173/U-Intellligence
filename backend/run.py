"""
Run script for U-Intelligence backend
"""
import os
import sys
from pathlib import Path

# Change to project root directory
project_root = Path(__file__).parent.parent
os.chdir(project_root)
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

