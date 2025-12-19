"""Pydantic models for API requests and responses"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ContentType(str, Enum):
    """Content type enumeration"""
    FLASHCARDS = "flashcards"
    INFOGRAPHICS = "infographics"
    VIDEO_SCRIPT = "video_script"
    PODCAST = "podcast"

class UploadResponse(BaseModel):
    """Response model for file upload"""
    job_id: str
    message: str
    files_uploaded: int

class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    status: JobStatus
    progress: float
    total_images: int
    processed_images: int
    message: Optional[str] = None

class TranscriptionResult(BaseModel):
    """Individual transcription result"""
    filename: str
    text: str
    success: bool
    error: Optional[str] = None

class JobResultsResponse(BaseModel):
    """Response model for job results"""
    job_id: str
    status: JobStatus
    results: List[TranscriptionResult]
    compiled_text: Optional[str] = None

class ContentGenerationRequest(BaseModel):
    """Request model for content generation"""
    job_id: str
    content_types: List[ContentType]
    customizations: Optional[Dict[str, Any]] = None

class ContentGenerationResponse(BaseModel):
    """Response model for content generation"""
    job_id: str
    content_types: List[ContentType]
    files: Dict[str, str]  # content_type -> file_path
    message: str

