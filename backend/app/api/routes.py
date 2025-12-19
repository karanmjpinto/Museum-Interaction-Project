"""API routes for the application"""
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
import json

from backend.app.api.models import (
    UploadResponse, JobStatusResponse, JobResultsResponse,
    ContentGenerationRequest, ContentGenerationResponse,
    JobStatus, ContentType
)
from backend.app.services.transcriber import TranscriptionService
from backend.app.services.content_generator import ContentGenerator
from backend.app.core.config import settings

router = APIRouter()

# In-memory job storage (in production, use Redis or database)
jobs = {}

def process_transcription_job(job_id: str, image_dir: Path):
    """Background task to process transcription"""
    try:
        jobs[job_id]["status"] = JobStatus.PROCESSING
        jobs[job_id]["message"] = "Processing images..."
        
        service = TranscriptionService(job_id=job_id)
        results, compiled_text = service.process_images(image_dir, output_filename="transcription")
        
        jobs[job_id]["status"] = JobStatus.COMPLETED
        jobs[job_id]["results"] = results
        jobs[job_id]["compiled_text"] = compiled_text
        jobs[job_id]["processed_images"] = len(results)
        jobs[job_id]["message"] = "Transcription completed successfully"
        
    except Exception as e:
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["message"] = f"Error: {str(e)}"

@router.post("/upload", response_model=UploadResponse)
async def upload_images(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload images for transcription
    
    Args:
        files: List of image files to upload
        background_tasks: FastAPI background tasks
        
    Returns:
        Upload response with job_id
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Validate file types
    for file in files:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file_ext}. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )
    
    # Create job
    job_id = str(uuid.uuid4())
    job_dir = settings.UPLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded files
    saved_files = []
    for file in files:
        file_path = job_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} exceeds maximum size of {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
                )
            f.write(content)
        saved_files.append(file.filename)
    
    # Initialize job tracking
    jobs[job_id] = {
        "status": JobStatus.PENDING,
        "total_images": len(files),
        "processed_images": 0,
        "results": None,
        "compiled_text": None,
        "message": "Files uploaded, ready to process"
    }
    
    # Start background processing
    if background_tasks:
        background_tasks.add_task(process_transcription_job, job_id, job_dir)
    
    return UploadResponse(
        job_id=job_id,
        message="Files uploaded successfully",
        files_uploaded=len(files)
    )

@router.post("/transcribe/{job_id}")
async def start_transcription(job_id: str, background_tasks: BackgroundTasks):
    """
    Start transcription for uploaded images
    
    Args:
        job_id: Job identifier from upload
        background_tasks: FastAPI background tasks
        
    Returns:
        Status response
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if jobs[job_id]["status"] != JobStatus.PENDING:
        raise HTTPException(status_code=400, detail="Job already processed or processing")
    
    # Find the upload directory
    job_dir = settings.UPLOAD_DIR / job_id
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Upload directory not found")
    
    # Start processing
    background_tasks.add_task(process_transcription_job, job_id, job_dir)
    
    return {"message": "Transcription started", "job_id": job_id}

@router.get("/job/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get status of a transcription job
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job status response
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    progress = 0.0
    if job["total_images"] > 0:
        progress = (job["processed_images"] / job["total_images"]) * 100
    
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=progress,
        total_images=job["total_images"],
        processed_images=job["processed_images"],
        message=job.get("message")
    )

@router.get("/job/{job_id}/results", response_model=JobResultsResponse)
async def get_job_results(job_id: str):
    """
    Get transcription results
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job results response
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    from backend.app.api.models import TranscriptionResult
    
    results = [
        TranscriptionResult(**result) for result in job["results"]
    ]
    
    return JobResultsResponse(
        job_id=job_id,
        status=job["status"],
        results=results,
        compiled_text=job.get("compiled_text")
    )

@router.post("/generate-content", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest):
    """
    Generate educational content from transcription
    
    Args:
        request: Content generation request
        
    Returns:
        Content generation response
    """
    if request.job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[request.job_id]
    
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Transcription must be completed first")
    
    if not job.get("compiled_text"):
        raise HTTPException(status_code=400, detail="No transcription text available")
    
    # Generate content
    generator = ContentGenerator()
    output_dir = settings.OUTPUT_DIR / request.job_id / "generated_content"
    
    try:
        generated_files = generator.generate_content(
            transcription_text=job["compiled_text"],
            content_types=request.content_types,
            output_dir=output_dir
        )
        
        return ContentGenerationResponse(
            job_id=request.job_id,
            content_types=request.content_types,
            files=generated_files,
            message="Content generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@router.get("/download/{job_id}/{file_type}")
async def download_file(job_id: str, file_type: str):
    """
    Download generated files
    
    Args:
        job_id: Job identifier
        file_type: Type of file to download (transcription, flashcards, infographics, etc.)
        
    Returns:
        File download
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Determine file path based on type
    if file_type == "transcription":
        file_path = settings.OUTPUT_DIR / job_id / "transcription.txt"
    elif file_type == "flashcards":
        file_path = settings.OUTPUT_DIR / job_id / "generated_content" / "flashcards.json"
    elif file_type == "infographics":
        file_path = settings.OUTPUT_DIR / job_id / "generated_content" / "infographic.md"
    elif file_type == "video_script":
        file_path = settings.OUTPUT_DIR / job_id / "generated_content" / "video_script.txt"
    elif file_type == "podcast":
        file_path = settings.OUTPUT_DIR / job_id / "generated_content" / "podcast_script.txt"
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream"
    )

