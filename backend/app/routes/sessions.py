"""
Session Management API Routes
Handles session creation, updates, and restoration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import json

from app.database import get_db
from app.models import Session as SessionModel, SessionFile, ExtractedBlock, FileMetadata
from app.schemas.v2_schemas import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionDetail
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new session"""
    # Convert metadata dict to JSON string
    metadata_json = json.dumps(session_data.metadata) if session_data.metadata else None
    
    new_session = SessionModel(
        name=session_data.name,
        session_metadata=metadata_json
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return SessionResponse(
        id=new_session.id,
        name=new_session.name,
        created_at=new_session.created_at,
        updated_at=new_session.updated_at,
        metadata=session_data.metadata,
        file_count=0,
        block_count=0
    )


@router.get("/", response_model=List[SessionResponse])
def list_sessions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all sessions with file and block counts"""
    sessions = db.query(SessionModel).order_by(
        SessionModel.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    response = []
    for session in sessions:
        # Count files in session
        file_count = db.query(SessionFile).filter(
            SessionFile.session_id == session.id
        ).count()
        
        # Count blocks in session
        block_count = db.query(ExtractedBlock).filter(
            ExtractedBlock.session_id == session.id
        ).count()
        
        # Parse metadata
        metadata = json.loads(session.session_metadata) if session.session_metadata else None
        
        response.append(SessionResponse(
            id=session.id,
            name=session.name,
            created_at=session.created_at,
            updated_at=session.updated_at,
            metadata=metadata,
            file_count=file_count,
            block_count=block_count
        ))
    
    return response


@router.get("/{session_id}", response_model=SessionDetail)
def get_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get session details with file list"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get file IDs in this session
    file_ids = [
        sf.file_id for sf in db.query(SessionFile).filter(
            SessionFile.session_id == session_id
        ).all()
    ]
    
    # Count blocks
    block_count = db.query(ExtractedBlock).filter(
        ExtractedBlock.session_id == session_id
    ).count()
    
    # Parse metadata
    metadata = json.loads(session.session_metadata) if session.session_metadata else None
    
    return SessionDetail(
        id=session.id,
        name=session.name,
        created_at=session.created_at,
        updated_at=session.updated_at,
        metadata=metadata,
        file_count=len(file_ids),
        block_count=block_count,
        files=file_ids
    )


@router.put("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int,
    session_update: SessionUpdate,
    db: Session = Depends(get_db)
):
    """Update session name or metadata"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Update fields if provided
    if session_update.name is not None:
        session.name = session_update.name
    
    if session_update.metadata is not None:
        session.session_metadata = json.dumps(session_update.metadata)
    
    db.commit()
    db.refresh(session)
    
    # Get counts
    file_count = db.query(SessionFile).filter(
        SessionFile.session_id == session_id
    ).count()
    
    block_count = db.query(ExtractedBlock).filter(
        ExtractedBlock.session_id == session_id
    ).count()
    
    metadata = json.loads(session.session_metadata) if session.session_metadata else None
    
    return SessionResponse(
        id=session.id,
        name=session.name,
        created_at=session.created_at,
        updated_at=session.updated_at,
        metadata=metadata,
        file_count=file_count,
        block_count=block_count
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Delete a session (files and blocks remain, just unlinked)"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Delete session (cascades to session_files via foreign key)
    db.delete(session)
    db.commit()
    
    return None


@router.post("/{session_id}/files/{file_id}", status_code=status.HTTP_201_CREATED)
def add_file_to_session(
    session_id: int,
    file_id: int,
    db: Session = Depends(get_db)
):
    """Add a file to a session"""
    # Verify session exists
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Verify file exists
    file = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if already added
    existing = db.query(SessionFile).filter(
        SessionFile.session_id == session_id,
        SessionFile.file_id == file_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="File already in session"
        )
    
    # Add file to session
    session_file = SessionFile(session_id=session_id, file_id=file_id)
    db.add(session_file)
    
    # Update all blocks from this file to link to session
    db.query(ExtractedBlock).filter(
        ExtractedBlock.file_id == file_id
    ).update({ExtractedBlock.session_id: session_id})
    
    db.commit()
    
    return {"message": "File added to session", "file_id": file_id}


@router.delete("/{session_id}/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_file_from_session(
    session_id: int,
    file_id: int,
    db: Session = Depends(get_db)
):
    """Remove a file from a session"""
    session_file = db.query(SessionFile).filter(
        SessionFile.session_id == session_id,
        SessionFile.file_id == file_id
    ).first()
    
    if not session_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not in session"
        )
    
    # Remove session link from blocks
    db.query(ExtractedBlock).filter(
        ExtractedBlock.file_id == file_id,
        ExtractedBlock.session_id == session_id
    ).update({ExtractedBlock.session_id: None})
    
    db.delete(session_file)
    db.commit()
    
    return None
