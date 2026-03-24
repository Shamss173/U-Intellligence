"""
File upload router
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.services.rag_service import rag_service
import os
import aiofiles
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{department_id}")
async def upload_file(
    department_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and ingest a document for a specific department
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Create department-specific directory
        dept_dir = os.path.join(settings.DEPARTMENTS_STORAGE_BASE, department_id)
        os.makedirs(dept_dir, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(dept_dir, safe_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            
            # Check file size
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
                )
            
            await f.write(content)
        
        # Prepare metadata
        metadata = {
            "filename": file.filename,
            "upload_date": datetime.now().isoformat(),
            "department_id": department_id,
            "file_size": len(content),
            "file_type": file_ext
        }
        
        # Ingest into RAG service
        ingestion_success = await rag_service.ingest_document(
            department_id=department_id,
            file_path=file_path,
            metadata=metadata
        )
        
        if not ingestion_success:
            # If ingestion fails, we still keep the file but log it
            logger.warning(f"RAG ingestion failed for file {file_path}, but file was saved")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "File uploaded and ingested successfully",
                "department_id": department_id,
                "filename": file.filename,
                "file_path": file_path,
                "metadata": metadata,
                "rag_ingested": ingestion_success
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in file upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{department_id}/files")
async def list_files(department_id: str):
    """List uploaded files for a department"""
    try:
        dept_dir = os.path.join(settings.DEPARTMENTS_STORAGE_BASE, department_id)
        
        if not os.path.exists(dept_dir):
            return {"files": []}
        
        files = []
        for filename in os.listdir(dept_dir):
            file_path = os.path.join(dept_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                # Extract original filename (remove timestamp prefix)
                original_name = filename.split('_', 1)[1] if '_' in filename else filename
                files.append({
                    "filename": filename,
                    "original_filename": original_name,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "uploaded": datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
        
        # Sort by most recent first
        files.sort(key=lambda x: x['modified'], reverse=True)
        return {"files": files}
    
    except Exception as e:
        logger.error(f"Error listing files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{department_id}/files/{filename}")
async def delete_file(department_id: str, filename: str):
    """Delete a file from department storage"""
    try:
        dept_dir = os.path.join(settings.DEPARTMENTS_STORAGE_BASE, department_id)
        file_path = os.path.join(dept_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete from file system
        os.remove(file_path)
        
        # Delete from RAG service if enabled
        await rag_service.delete_document(department_id, filename)
        
        return {"message": "File deleted successfully", "filename": filename}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
