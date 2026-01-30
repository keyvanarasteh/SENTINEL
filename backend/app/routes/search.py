"""
Search Router - Advanced Search & Filtering
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import ExtractedBlock, FileMetadata
from app.schemas.v2_schemas import SearchResponse, SearchResult

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search_blocks(
    q: Optional[str] = None,
    languages: Optional[List[str]] = Query(None),
    min_confidence: Optional[float] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    session_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    """
    Search extracted blocks with advanced filtering.
    """
    # Base query joined with FileMetadata for filename and dates
    query = db.query(ExtractedBlock).join(FileMetadata)
    
    # 1. Text Search (SQL LIKE)
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                ExtractedBlock.content.ilike(search_term),
                FileMetadata.filename.ilike(search_term)
            )
        )
    
    # 2. Language Filter
    if languages:
        query = query.filter(ExtractedBlock.language.in_(languages))
    
    # 3. Confidence Filter
    if min_confidence is not None:
        query = query.filter(ExtractedBlock.confidence_score >= min_confidence)
    
    # 4. Date Range Filter
    if date_from:
        query = query.filter(FileMetadata.upload_date >= date_from)
    if date_to:
        query = query.filter(FileMetadata.upload_date <= date_to)
        
    # 5. Session Filter
    if session_id:
        query = query.filter(ExtractedBlock.session_id == session_id)
    
    # Calculate Total Results (before pagination)
    total_results = query.count()
    
    # Ordering
    # Prioritize confidence, then date
    query = query.order_by(
        desc(ExtractedBlock.confidence_score),
        desc(FileMetadata.upload_date)
    )
    
    # Pagination
    offset = (page - 1) * per_page
    blocks = query.offset(offset).limit(per_page).all()
    
    # Construct Results
    results = []
    
    for block in blocks:
        # Simple match score calculation if query exists
        match_score = 0.0
        if q:
            # Basic term frequency heuristic
            term_count = block.content.lower().count(q.lower())
            filename_match = 1.0 if q.lower() in block.file.filename.lower() else 0.0
            match_score = (term_count * 0.1) + (filename_match * 0.5) + (block.confidence_score * 0.4)
        else:
            match_score = block.confidence_score
            
        results.append(SearchResult(
            block_id=block.id,
            content=block.content,
            language=block.language,
            confidence_score=block.confidence_score,
            file_id=block.file_id,
            filename=block.file.filename,
            created_at=block.file.upload_date,
            match_score=round(match_score, 2)
        ))
        
    # Sort results by match_score if query provided (client-side sort also possible)
    if q:
        results.sort(key=lambda x: x.match_score, reverse=True)
        
    return SearchResponse(
        total_results=total_results,
        results=results,
        page=page,
        per_page=per_page
    )
