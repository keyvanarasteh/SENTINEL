"""
Export Route - Generate ZIP Archive with Categorized Files
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import zipfile
import json

from app.database import get_db
from app.models import ExtractedBlock, FileMetadata, BlockStatus

from typing import Optional
from app.services.export_service import ExportService

router = APIRouter(prefix="/api", tags=["export"])

EXPORT_DIR = Path(__file__).parent.parent.parent.parent / "data" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
export_service = ExportService(EXPORT_DIR)


@router.get("/export/{file_id}")
def export_blocks(
    file_id: int, 
    format: str = "zip", 
    db: Session = Depends(get_db)
):
    """
    Export extracted blocks.
    
    Args:
        file_id (int): File ID to export.
        format (str): Export format ('zip', 'jsonl', 'parquet').
    """
    # Get file metadata
    file_meta = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    if not file_meta:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get accepted blocks
    blocks = db.query(ExtractedBlock).filter(
        ExtractedBlock.file_id == file_id,
        ExtractedBlock.status == BlockStatus.ACCEPTED
    ).all()
    
    if not blocks:
        raise HTTPException(
            status_code=404,
            detail="No accepted blocks found. Please review and accept blocks first."
        )
    
    try:
        if format == "zip":
            file_path = export_service.generate_zip(file_meta, blocks)
            media_type = "application/zip"
            filename = file_path.name
        elif format == "jsonl":
            file_path = export_service.generate_jsonl(file_meta, blocks)
            media_type = "application/x-jsonlines"
            filename = file_path.name
        elif format == "parquet":
            file_path = export_service.generate_parquet(file_meta, blocks)
            media_type = "application/vnd.apache.parquet"
            filename = file_path.name
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
            
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
