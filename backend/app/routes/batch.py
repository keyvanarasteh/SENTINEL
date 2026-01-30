"""
Batch Processing API Routes
Upload and process multiple files simultaneously
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
import hashlib
from datetime import datetime

from app.database import get_db
from app.models import FileMetadata
from app.schemas.v2_schemas import BatchUploadResponse, BatchStatusResponse, BatchFileStatus
from app.engine.batch_processor import BatchProcessor

router = APIRouter(prefix="/api/batch", tags=["batch-processing"])

# Global batch processor instances (keyed by batch_id)
batch_processors = {}


@router.post("/upload", response_model=BatchUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_batch(
    files: List[UploadFile] = File(...),
    session_id: int = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Upload multiple files for batch processing
    
    - Maximum 20 files per batch
    - Supported formats: PDF, DOCX, TXT
    - Processing happens asynchronously
    """
    # Validate file count
    if len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file is required"
        )
    
    if len(files) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 20 files allowed per batch"
        )
    
    # Generate batch ID
    batch_id = str(uuid.uuid4())
    
    # Upload directory
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_ids = []
    
    # Save each file
    for file in files:
        # Validate file type
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ['pdf', 'docx', 'txt', 'md', 'log', 'conf', 'json', 'yaml', 'xml']:
            continue  # Skip unsupported files
        
        # Read file content
        content = await file.read()
        
        # Calculate hash
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Check for duplicates
        existing_file = db.query(FileMetadata).filter(
            FileMetadata.file_hash == file_hash
        ).first()
        
        if existing_file:
            file_ids.append(existing_file.id)
            continue
        
        # Generate unique filename
        timestamp = int(datetime.utcnow().timestamp())
        unique_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Create database record
        file_metadata = FileMetadata(
            filename=unique_filename,
            original_filename=file.filename,
            file_type=file_extension,
            file_size=len(content),
            file_hash=file_hash,
            batch_id=batch_id,
            processing_status="pending"
        )
        
        db.add(file_metadata)
        db.commit()
        db.refresh(file_metadata)
        
        file_ids.append(file_metadata.id)
    
    # Initialize batch processor
    processor = BatchProcessor(db)
    batch_processors[batch_id] = processor
    
    # Start async processing in background
    import asyncio
    asyncio.create_task(
        processor.process_batch(batch_id, file_ids, session_id)
    )
    
    return BatchUploadResponse(
        batch_id=batch_id,
        total_files=len(file_ids),
        processing_status="in_progress"
    )


@router.get("/{batch_id}/status", response_model=BatchStatusResponse)
def get_batch_status(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """Get current processing status of a batch"""
    # Check if batch exists
    processor = batch_processors.get(batch_id)
    
    if not processor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Get status
    status_data = processor.get_batch_status(batch_id)
    
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch status not available"
        )
    
    # Build file statuses
    file_statuses = []
    for file_id, file_status in status_data["file_statuses"].items():
        # Get filename from database
        file = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
        
        file_statuses.append(BatchFileStatus(
            file_id=file_id,
            filename=file.original_filename if file else "unknown",
            status=file_status["status"],
            blocks_extracted=file_status.get("blocks_extracted", 0),
            error_message=file_status.get("error")
        ))
    
    # Determine overall status
    if status_data["in_progress"]:
        overall_status = "in_progress"
    elif status_data["failed_files"] > 0:
        overall_status = "partial_failure"
    else:
        overall_status = "complete"
    
    return BatchStatusResponse(
        batch_id=batch_id,
        total_files=status_data["total_files"],
        completed_files=status_data["completed_files"],
        failed_files=status_data["failed_files"],
        overall_status=overall_status,
        files=file_statuses
    )


@router.get("/{batch_id}/export")
def export_batch(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """Export all extracted blocks from a batch as ZIP"""
    # Get all files in batch
    files = db.query(FileMetadata).filter(
        FileMetadata.batch_id == batch_id
    ).all()
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found or no files"
        )
    
    # TODO: Implement ZIP export for entire batch
    # This will be similar to single file export but across all files
    
    return {
        "message": "Batch export will be implemented",
        "batch_id": batch_id,
        "file_count": len(files)
    }
