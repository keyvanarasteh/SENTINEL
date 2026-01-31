"""
Extract Route - Trigger Extraction Process
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
import time

from app.database import get_db
from app.models import FileMetadata, ExtractedBlock, BlockStatus
from app.schemas.schemas import ExtractionResponse, ExtractedBlockSchema, BatchDeleteRequest, UpdateBlockRequest
from app.engine.normalizer import FileNormalizer
from app.engine.segmenter import Segmenter
from app.engine.validator import Validator
from app.engine.filter import PrecisionFilter

router = APIRouter(prefix="/api", tags=["extract"])

UPLOAD_DIR = Path(__file__).parent.parent.parent.parent / "data" / "uploads"


@router.post("/extract/{file_id}", response_model=ExtractionResponse)
def extract_file(file_id: int, db: Session = Depends(get_db)):
    """
    Extract code blocks from uploaded file.
    
    Process:
    1. Load and normalize file
    2. Segment into candidate blocks
    3. Validate with hybrid engine
    4. Filter false positives
    5. Store results
    """
    start_time = time.time()
    
    # Get file metadata
    file_meta = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    if not file_meta:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if blocks already exist (avoid duplicate extraction)
    existing_blocks_count = db.query(ExtractedBlock).filter(ExtractedBlock.file_id == file_id).count()
    if existing_blocks_count > 0:
        db_blocks = db.query(ExtractedBlock).filter(ExtractedBlock.file_id == file_id).all()
        block_schemas = [
            ExtractedBlockSchema(
                id=block.id,
                content=block.content,
                language=block.language,
                block_type=block.block_type,
                confidence_score=block.confidence_score,
                validation_method=block.validation_method,
                start_line=block.start_line,
                end_line=block.end_line,
                status=block.status.value
            )
            for block in db_blocks
        ]
        return ExtractionResponse(
            file_id=file_id,
            filename=file_meta.original_filename,
            total_blocks=len(block_schemas),
            blocks=block_schemas,
            processing_time=0.0
        )

    # Determine file path (handled correctly for Git repos)
    if file_meta.original_path:
        file_path = Path(file_meta.original_path)
    else:
        file_path = UPLOAD_DIR / file_meta.filename
        
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Initialize components
    normalizer = FileNormalizer()
    segmenter = Segmenter()
    validator = Validator()
    precision_filter = PrecisionFilter()
    
    # Step 1: Normalize
    try:
        normalized_data = normalizer.normalize_file(str(file_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Normalization failed: {e}")
    
    # Step 2: Segment
    candidate_blocks = segmenter.segment(
        normalized_data['content'], 
        language=file_meta.file_type,
        filename=file_meta.original_filename
    )
    
    # Step 3: Validate
    validation_results = []
    for block in candidate_blocks:
        result = validator.validate_block(block, filename=file_meta.original_filename)
        validation_results.append(result)
    
    # Step 4: Filter
    accepted_blocks = precision_filter.batch_filter(validation_results)
    
    # Step 5: Store in database
    db_blocks = []
    for block_data in accepted_blocks:
        db_block = ExtractedBlock(
            file_id=file_id,
            content=block_data['content'],
            language=block_data.get('language'),
            block_type=block_data['block_type'],
            confidence_score=block_data['confidence_score'],
            validation_method=block_data.get('validation_method'),
            start_line=block_data['start_line'],
            end_line=block_data['end_line'],
            status=BlockStatus.PENDING
        )
        db.add(db_block)
        db_blocks.append(db_block)
    
    db.commit()
    
    # Refresh to get IDs
    for block in db_blocks:
        db.refresh(block)
    
    processing_time = time.time() - start_time
    
    # Prepare response
    block_schemas = [
        ExtractedBlockSchema(
            id=block.id,
            content=block.content,
            language=block.language,
            block_type=block.block_type,
            confidence_score=block.confidence_score,
            validation_method=block.validation_method,
            start_line=block.start_line,
            end_line=block.end_line,
            status=block.status.value
        )
        for block in db_blocks
    ]
    
    # Prepare stats
    ast_count = sum(1 for b in db_blocks if b.validation_method != 'fallback_regex')
    fallback_count = sum(1 for b in db_blocks if b.validation_method == 'fallback_regex')
    
    stats = {
        "ast_parsed": ast_count,
        "fallback_extracted": fallback_count,
        "total_extracted": len(db_blocks)
    }

    return ExtractionResponse(
        file_id=file_id,
        filename=file_meta.original_filename,
        total_blocks=len(block_schemas),
        blocks=block_schemas,
        processing_time=round(processing_time, 3),
        stats=stats
    )


@router.put("/blocks/{block_id}", response_model=ExtractedBlockSchema)
def update_block(
    block_id: int, 
    request: UpdateBlockRequest, 
    db: Session = Depends(get_db)
):
    """Update an extracted block's content and language."""
    block = db.query(ExtractedBlock).filter(ExtractedBlock.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    block.content = request.content
    if request.language:
        block.language = request.language
    
    # Update stats
    block.status = BlockStatus.MODIFIED
    
    db.commit()
    db.refresh(block)
    
    return ExtractedBlockSchema(
        id=block.id,
        content=block.content,
        language=block.language,
        block_type=block.block_type,
        confidence_score=block.confidence_score,
        validation_method=block.validation_method,
        start_line=block.start_line,
        end_line=block.end_line,
        status=block.status.value
    )

@router.delete("/blocks/{block_id}", status_code=204)
def delete_block(block_id: int, db: Session = Depends(get_db)):
    """Delete an extracted block."""
    block = db.query(ExtractedBlock).filter(ExtractedBlock.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
        
    db.delete(block)
    db.commit()
    return None


@router.post("/blocks/batch-delete")
def batch_delete_blocks(request: BatchDeleteRequest, db: Session = Depends(get_db)):
    """Delete multiple blocks by ID."""
    if not request.block_ids:
        return {"deleted_count": 0}
        
    # delete() with synchronize_session=False is faster for bulk
    deleted_count = db.query(ExtractedBlock).filter(
        ExtractedBlock.id.in_(request.block_ids)
    ).delete(synchronize_session=False)
    
    db.commit()
    return {"deleted_count": deleted_count}


@router.get("/files/{file_id}/content")
def get_file_content(file_id: int, db: Session = Depends(get_db)):
    """Get raw content of a file by ID."""
    file_meta = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    if not file_meta:
        raise HTTPException(status_code=404, detail="File not found")
        
    # Check if absolute path is stored (git files) or construct from upload dir (uploaded files)
    if file_meta.original_path:
        path = Path(file_meta.original_path)
    else:
        path = UPLOAD_DIR / file_meta.filename
        
        
    # SECURITY: Prevent Path Traversal
    try:
        # Resolve to absolute path to handle any '..'
        resolved_path = path.resolve()
        # Ensure path is strictly within UPLOAD_DIR (or temp dir for git repos)
        # Note: Git repos use OS temp dir, so we check if it exists and is a file.
        # Ideally we should validate it's inside allowed roots, but for now specific check:
        # If it's a git file, it might be in /tmp. If it's an upload, it's in UPLOAD_DIR.
        # We enforce that the file MUST exist and be a FILE (not directory).
        
        # Additional check: If it's supposed to be an uploaded file, force containment
        if not file_meta.original_path and not resolved_path.is_relative_to(UPLOAD_DIR.resolve()):
             print(f"Security Alert: Path traversal attempt blocked: {path}")
             raise HTTPException(status_code=403, detail="Access denied")
             
    except ValueError:
        # is_relative_to raises ValueError if not related
        if not file_meta.original_path:
            raise HTTPException(status_code=403, detail="Access denied")

    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found on disk")
        
    try:
        # Simple read, assuming text files for now given supported extensions
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {e}")
