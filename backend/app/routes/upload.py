"""
Upload Route - File Upload Endpoint
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil
from pathlib import Path
import hashlib

from app.database import get_db
from app.models import FileMetadata
from app.schemas.schemas import FileUploadResponse

router = APIRouter(prefix="/api", tags=["upload"])

# Use proper path relative to project root
import os
import re
import unicodedata

UPLOAD_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))) / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def secure_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and unsafe characters.
    """
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    filename = re.sub(r'[^\w\.\-]', '_', filename)
    filename = filename.strip('._')
    return filename


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a file for extraction.
    
    Supports: PDF, DOCX, TXT, MD, LOG, SH, BAT, CONFIG, INI, YAML, JSON, XML
    """
    # Validate file type
    allowed_extensions = {
        '.pdf', '.docx', '.txt', '.md', '.log', '.sh', '.bat',
        '.config', '.ini', '.env', '.yaml', '.yml', '.json', '.xml',
        '.html', '.htm', '.css', '.js', '.jsx', '.ts', '.tsx', '.csv', '.sql',
        '.py', '.rb', '.php', '.java', '.c', '.cpp', '.h', '.hpp', '.go', '.rs',
        '.kt', '.swift', '.m', '.dart', '.vue', '.scala', '.r'
    }
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
        )
    
    # Read file content to check size and calculate hash
    content = await file.read()
    file_size = len(content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {file_size} bytes > {MAX_FILE_SIZE} bytes (50MB)"
        )
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    # Calculate file hash for deduplication
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Check if file already exists
    existing_file = db.query(FileMetadata).filter(
        FileMetadata.file_hash == file_hash
    ).first()
    
    if existing_file:
        return FileUploadResponse(
            file_id=existing_file.id,
            filename=existing_file.filename,
            file_type=existing_file.file_type,
            file_size=existing_file.file_size,
            file_hash=existing_file.file_hash,
            message="File already exists (duplicate detected)"
        )
    
    # Save file to disk with Hardening
    # 1. Sanitize filename
    safe_name = secure_filename(file.filename)
    safe_filename = f"{file_hash[:16]}_{safe_name}"
    
    file_path = UPLOAD_DIR / safe_filename
    
    with open(file_path, 'wb') as f:
        f.write(content)

    # 3. Strip Executable Permissions (Prevent Code Execution)
    # chmod 644: Owner read/write, Group read, Others read. NO EXECUTE.
    try:
        os.chmod(file_path, 0o644)
    except Exception as e:
        print(f"Warning: Failed to chmod file {file_path}: {e}")
    
    # Save metadata to database
    file_metadata = FileMetadata(
        filename=safe_filename,
        original_filename=safe_name, # Store sanitized name
        file_type=file_ext.lstrip('.'),  # Remove leading dot
        file_size=file_size,
        file_hash=file_hash
    )
    
    db.add(file_metadata)
    db.commit()
    db.refresh(file_metadata)
    
    return FileUploadResponse(
        file_id=file_metadata.id,
        filename=file_metadata.filename,
        file_type=file_metadata.file_type,
        file_size=file_metadata.file_size,
        file_hash=file_metadata.file_hash
    )
