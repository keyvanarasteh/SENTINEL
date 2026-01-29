"""
Text Input API Routes
Process pasted text and markdown directly without file upload
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import hashlib

from app.database import get_db
from app.models import TextInput, ExtractedBlock
from app.schemas.v2_schemas import TextInputCreate, TextInputResponse
from app.schemas.schemas import ExtractedBlockSchema
from app.engine.normalizer import FileNormalizer
from app.engine.segmenter import Segmenter
from app.engine.validator import Validator
from app.engine.filter import PrecisionFilter
from typing import List

router = APIRouter(prefix="/api/input", tags=["text-input"])


@router.post("/text", response_model=dict)
def process_text_input(
    text_data: TextInputCreate,
    session_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Process pasted text or markdown content
    Returns extracted blocks without saving to file_metadata table
    """
    # Calculate hash for deduplication
    content_hash = hashlib.sha256(text_data.content.encode()).hexdigest()
    
    # Check if already processed
    existing = db.query(TextInput).filter(TextInput.file_hash == content_hash).first()
    
    if existing:
        # Return previously extracted blocks
        blocks = db.query(ExtractedBlock).filter(
            ExtractedBlock.file_id == existing.id  # Reusing file_id for text_input_id
        ).all()
        
        return {
            "text_input_id": existing.id,
            "source_type": existing.source_type,
            "created_at": existing.created_at,
            "blocks": [ExtractedBlockSchema.model_validate(b.__dict__) for b in blocks],
            "cached": True
        }
    
    # Save text input
    text_input = TextInput(
        content=text_data.content,
        source_type=text_data.source_type,
        file_hash=content_hash
    )
    db.add(text_input)
    db.commit()
    db.refresh(text_input)
    
    # Process through extraction pipeline
    try:
        # 1. Normalization (minimal for text input)
        normalizer = FileNormalizer()
        normalized_text = normalizer._normalize_text(text_data.content)
        
        # 2. Segmentation
        segmenter = Segmenter()
        segments = segmenter.segment(normalized_text)
        
        # 3. Validation
        validator = Validator(db)
        validated_blocks = []
        
        for segment in segments:
            result = validator.validate_block(segment['content'])
            if result['is_valid']:
                validated_blocks.append({
                    'content': segment['content'],
                    'language': result.get('language'),
                    'block_type': result.get('type', 'code'),
                    'confidence_score': result.get('confidence', 0),
                    'validation_method': result.get('method', 'unknown'),
                    'start_line': segment.get('start_line'),
                    'end_line': segment.get('end_line')
                })
        
        # 4. Precision filtering
        precision_filter = PrecisionFilter()
        final_blocks = []
        
        for block_data in validated_blocks:
            filter_result = precision_filter.filter_block(
                content=block_data['content'],
                language=block_data['language'],
                confidence=block_data['confidence_score']
            )
            
            if filter_result['should_keep']:
                # Save to database
                extracted_block = ExtractedBlock(
                    file_id=text_input.id,  # Link to text_input
                    session_id=session_id,
                    content=block_data['content'],
                    language=block_data['language'],
                    block_type=block_data['block_type'],
                    confidence_score=filter_result.get('adjusted_confidence', block_data['confidence_score']),
                    validation_method=block_data['validation_method'],
                    start_line=block_data.get('start_line'),
                    end_line=block_data.get('end_line')
                )
                db.add(extracted_block)
                final_blocks.append(extracted_block)
        
        db.commit()
        
        #  Refresh to get IDs
        for block in final_blocks:
            db.refresh(block)
        
        return {
            "text_input_id": text_input.id,
            "source_type": text_input.source_type,
            "created_at": text_input.created_at,
            "blocks": [ExtractedBlockSchema.model_validate(b.__dict__) for b in final_blocks],
            "cached": False
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}"
        )


@router.get("/history", response_model=List[TextInputResponse])
def get_text_input_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get history of text inputs"""
    inputs = db.query(TextInput).order_by(
        TextInput.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [TextInputResponse.model_validate(inp.__dict__) for inp in inputs]


@router.get("/{text_input_id}/blocks", response_model=List[ExtractedBlockSchema])
def get_text_input_blocks(
    text_input_id: int,
    db: Session = Depends(get_db)
):
    """Get extracted blocks for a text input"""
    text_input = db.query(TextInput).filter(TextInput.id == text_input_id).first()
    
    if not text_input:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Text input not found"
        )
    
    blocks = db.query(ExtractedBlock).filter(
        ExtractedBlock.file_id == text_input_id
    ).all()
    
    return [ExtractedBlockSchema.model_validate(b.__dict__) for b in blocks]


@router.delete("/{text_input_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_text_input(
    text_input_id: int,
    db: Session = Depends(get_db)
):
    """Delete a text input and its extracted blocks"""
    text_input = db.query(TextInput).filter(TextInput.id == text_input_id).first()
    
    if not text_input:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Text input not found"
        )
    
    # Delete associated blocks
    db.query(ExtractedBlock).filter(
        ExtractedBlock.file_id == text_input_id
    ).delete()
    
    # Delete text input
    db.delete(text_input)
    db.commit()
    
    return None
