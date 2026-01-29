"""
Pydantic schemas for API request/response models.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FileUploadResponse(BaseModel):
    """Response for file upload."""
    file_id: int
    filename: str
    file_type: str
    file_size: int
    file_hash: str
    message: str = "File uploaded successfully"


class ExtractedBlockSchema(BaseModel):
    """Schema for an extracted block."""
    id: Optional[int] = None
    content: str
    language: Optional[str] = None
    block_type: str  # code, config, log, structured
    confidence_score: float
    validation_method: Optional[str] = None
    start_line: int
    end_line: int
    status: str = "pending"


class ExtractionResponse(BaseModel):
    """Response for extraction endpoint."""
    file_id: int
    filename: str
    total_blocks: int
    blocks: List[ExtractedBlockSchema]
    processing_time: float


class FeedbackRequest(BaseModel):
    """Request for user feedback."""
    block_id: int
    action: str = Field(..., pattern="^(accept|reject|modify)$")
    corrected_language: Optional[str] = None
    corrected_type: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Response for feedback submission."""
    success: bool
    message: str
    updated_confidence: Optional[float] = None


class ExportResponse(BaseModel):
    """Response for export generation."""
    filename: str
    file_path: str
    total_files: int
    categories: dict
