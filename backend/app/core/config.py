"""Configuration management for the application"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # API Configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "localhost")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    
    # File paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "backend" / "uploads"
    OUTPUT_DIR: Path = BASE_DIR / "backend" / "outputs"
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    
    # File upload limits
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
    
    def __init__(self):
        """Initialize directories"""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        if not self.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

settings = Settings()

