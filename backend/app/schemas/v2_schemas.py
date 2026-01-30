"""
Pydantic schemas for v2.0 features
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================================================
# Session Schemas
# ============================================================================

class SessionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    metadata: Optional[dict] = None


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    metadata: Optional[dict] = None


class SessionResponse(SessionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    file_count: int = 0
    block_count: int = 0
    
    class Config:
        from_attributes = True


class SessionDetail(SessionResponse):
    files: List[int] = []  # List of file IDs
    
    class Config:
        from_attributes = True


#  ============================================================================
# Text Input Schemas
# ============================================================================

class TextInputCreate(BaseModel):
    content: str = Field(..., min_length=1)
    source_type: str = Field(default="paste", pattern="^(paste|markdown)$")


class TextInputResponse(BaseModel):
    id: int
    source_type: str
    created_at: datetime
    file_hash: str
    
    class Config:
        from_attributes = True


# ============================================================================
# Batch Processing Schemas
# ============================================================================

class BatchUploadResponse(BaseModel):
    batch_id: str
    total_files: int
    processing_status: str


class BatchFileStatus(BaseModel):
    file_id: int
    filename: str
    status: str  # pending, processing, complete, error
    blocks_extracted: int = 0
    error_message: Optional[str] = None


class BatchStatusResponse(BaseModel):
    batch_id: str
    total_files: int
    completed_files: int
    failed_files: int
    overall_status: str  # in_progress, complete, partial_failure
    files: List[BatchFileStatus]


# ============================================================================
# Analytics Schemas
# ============================================================================

class LanguageStats(BaseModel):
    language: str
    count: int
    percentage: float


class AnalyticsOverview(BaseModel):
    total_files: int
    total_blocks: int
    avg_confidence: float
    language_distribution: List[LanguageStats]


class DailyStats(BaseModel):
    date: str
    total_files: int
    total_blocks: int
    avg_confidence: float


class FileStats(BaseModel):
    file_id: int
    filename: str
    block_count: int
    language: Optional[str] = None


class AnalyticsTrends(BaseModel):
    daily_stats: List[DailyStats]
    date_range: str


# ============================================================================
# Search & Filter Schemas
# ============================================================================

class SearchFilters(BaseModel):
    query: Optional[str] = None
    languages: Optional[List[str]] = None
    min_confidence: Optional[float] = Field(None, ge=0, le=100)
    max_confidence: Optional[float] = Field(None, ge=0, le=100)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    session_id: Optional[int] = None


class SearchResult(BaseModel):
    block_id: int
    content: str
    language: Optional[str]
    confidence_score: float
    file_id: int
    filename: str
    created_at: datetime
    match_score: Optional[float] = None  # Relevance score for text search
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    total_results: int
    results: List[SearchResult]
    page: int = 1
    per_page: int = 20


# ============================================================================
# Git Integration Schemas
# ============================================================================

class GitAnalysisRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = None


class GitAnalysisRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = None


class GitFile(BaseModel):
    path: str
    id: int


class GitAnalysisResponse(BaseModel):
    batch_id: str
    message: str
    repo_name: str
    file_count: int
    files: List[GitFile] = []


class GitEstimateRequest(BaseModel):
    repo_url: str


class GitEstimateResponse(BaseModel):
    size_mb: float
    estimated_seconds: int
    file_count: Optional[int] = None

