"""Service wrapper for ImageTranscriber"""
import sys
from pathlib import Path

# Add parent directory to path to import image_transcriber
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
from image_transcriber import ImageTranscriber
from backend.app.core.config import settings

class TranscriptionService:
    """Service for handling image transcription"""
    
    def __init__(self, job_id: str, output_dir: str = None):
        """
        Initialize transcription service
        
        Args:
            job_id: Unique job identifier
            output_dir: Output directory (defaults to backend/outputs/job_id)
        """
        self.job_id = job_id
        self.output_dir = output_dir or str(settings.OUTPUT_DIR / job_id)
        self.transcriber = ImageTranscriber(
            api_key=settings.ANTHROPIC_API_KEY,
            output_dir=self.output_dir
        )
    
    def process_images(self, image_dir: Path, output_filename: str = "transcription"):
        """
        Process all images in a directory
        
        Args:
            image_dir: Directory containing images
            output_filename: Base name for output files
            
        Returns:
            Tuple of (results list, compiled text)
        """
        # Find all image files
        image_extensions = settings.ALLOWED_EXTENSIONS
        image_paths = [
            p for p in sorted(image_dir.iterdir()) 
            if p.suffix.lower() in image_extensions
        ]
        
        if not image_paths:
            return [], ""
        
        # Transcribe all images
        results = self.transcriber.transcribe_batch(image_paths)
        
        # Compile results
        compiled_text = self.transcriber.compile_results(results, title=f"Transcription - {self.job_id}")
        
        # Save outputs
        self.transcriber.save_output(compiled_text, output_filename)
        
        return results, compiled_text

