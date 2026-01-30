"""
System Routes - Maintenance and Admin tasks
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import shutil
import os
from pathlib import Path

from app.database import get_db
from app.models import (
    FileMetadata, ExtractedBlock, UserFeedback, 
    Session, SessionFile, ExtractionStats, TextInput
)
from app.services.git_service import GitService

router = APIRouter(prefix="/api/system", tags=["system"])

# Define paths (Must match other modules)
UPLOAD_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))) / "data" / "uploads"
GIT_TEMP_DIR = Path("/tmp/hpes_git_repos") # Default from GitService

@router.delete("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_system(db: Session = Depends(get_db)):
    """
    DANGER: Reset the entire system.
    1. Truncate all database tables.
    2. Delete all uploaded files.
    3. Delete all cloned repositories.
    """
    try:
        # 1. Database Cleanup
        # Order matters for foreign keys
        db.query(UserFeedback).delete()
        db.query(ExtractedBlock).delete()
        db.query(SessionFile).delete()
        db.query(Session).delete()
        db.query(FileMetadata).delete()
        db.query(ExtractionStats).delete()
        db.query(TextInput).delete()
        
        db.commit()
        
        # 2. File Cleanup - Uploads
        if UPLOAD_DIR.exists():
            # Delete contents but keep directory
            for item in UPLOAD_DIR.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception as e:
                    print(f"Failed to delete {item}: {e}")
                    
        # 3. File Cleanup - Git Repos
        if GIT_TEMP_DIR.exists():
            shutil.rmtree(GIT_TEMP_DIR)
            GIT_TEMP_DIR.mkdir(exist_ok=True)
            
        return None
        
    except Exception as e:
        db.rollback()
        print(f"System Reset Failed: {e}")
        raise HTTPException(status_code=500, detail=f"System reset failed: {str(e)}")
