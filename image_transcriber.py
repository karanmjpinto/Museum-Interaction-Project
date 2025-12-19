#!/usr/bin/env python3
"""
Image Transcription and Compilation Tool for NotebookLM
Processes multiple images, extracts text using Claude API, and compiles into podcast-ready format
"""

import os
import base64
from pathlib import Path
from typing import List, Dict
import anthropic
from PIL import Image
import io
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ImageTranscriber:
    def __init__(self, api_key: str = None, output_dir: str = "transcription_output"):
        """
        Initialize the transcriber
        
        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
            output_dir: Directory to save output files
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Set ANTHROPIC_API_KEY env var or pass api_key parameter")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def compress_image(self, image_path: Path, max_size_mb: float = 5.0, quality: int = 85) -> bytes:
        """
        Compress image if it's too large while maintaining readability
        Handles portrait, landscape, and rotated images automatically
        
        Args:
            image_path: Path to the image
            max_size_mb: Maximum size in MB
            quality: JPEG quality (1-100)
            
        Returns:
            Compressed image bytes
        """
        with Image.open(image_path) as img:
            # Handle EXIF orientation data (fixes rotated images from phones/cameras)
            try:
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass  # If EXIF handling fails, continue without it
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Log orientation for debugging
            orientation = "landscape" if img.width > img.height else "portrait" if img.height > img.width else "square"
            print(f"  → {orientation} ({img.width}x{img.height})")
            
            # Try original size first
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            
            # If still too large, resize intelligently
            if output.tell() > max_size_mb * 1024 * 1024:
                # For text readability, use higher max dimension
                # Portrait images often need more vertical pixels for text
                max_dimension = 2400  # Increased from 2048 for better text clarity
                ratio = min(max_dimension / img.width, max_dimension / img.height)
                if ratio < 1:
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    print(f"  → Resized to {new_size[0]}x{new_size[1]}")
                
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=quality, optimize=True)
            
            return output.getvalue()
    
    def encode_image(self, image_path: Path) -> tuple[str, str]:
        """
        Encode image to base64, compressing if necessary
        
        Returns:
            Tuple of (base64_string, media_type)
        """
        file_ext = image_path.suffix.lower()
        
        # For large or high-res images, compress first
        if file_ext in ['.jpg', '.jpeg', '.png', '.webp']:
            image_bytes = self.compress_image(image_path)
            media_type = "image/jpeg"
        else:
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            media_type = f"image/{file_ext[1:]}"
        
        return base64.b64encode(image_bytes).decode('utf-8'), media_type
    
    def transcribe_image(self, image_path: Path) -> Dict:
        """
        Transcribe a single image using Claude
        
        Returns:
            Dict with filename, text content, and any errors
        """
        try:
            print(f"Processing: {image_path.name}")
            
            base64_image, media_type = self.encode_image(image_path)
            
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": base64_image
                                }
                            },
                            {
                                "type": "text",
                                "text": """Please transcribe all the text you can see in this image, regardless of orientation (portrait, landscape, or rotated).
                                
Be thorough and accurate. If there are:
- Headings or titles, preserve them
- Bullet points or lists, maintain the structure  
- Tables or structured data, format them clearly
- Multiple columns, transcribe left to right, top to bottom
- Text in different orientations, transcribe it in reading order
- Any diagrams, charts, or images with labels, include the labels
- Handwritten notes or annotations, include those too
- Any rotated or angled text, transcribe it as you would read it

If the image is portrait/vertical (like a phone screenshot or vertical document), transcribe from top to bottom.
If the image is landscape/horizontal, transcribe left to right, top to bottom.

Please output just the transcribed text without any preamble or commentary."""
                            }
                        ]
                    }
                ]
            )
            
            text_content = message.content[0].text
            
            return {
                "filename": image_path.name,
                "text": text_content,
                "success": True,
                "error": None
            }
            
        except Exception as e:
            print(f"Error processing {image_path.name}: {str(e)}")
            return {
                "filename": image_path.name,
                "text": "",
                "success": False,
                "error": str(e)
            }
    
    def transcribe_batch(self, image_paths: List[Path], batch_size: int = 10) -> List[Dict]:
        """
        Transcribe multiple images in batches
        
        Args:
            image_paths: List of paths to images
            batch_size: Number of images to process before pausing
            
        Returns:
            List of transcription results
        """
        results = []
        total = len(image_paths)
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"\nProcessing image {i}/{total}")
            result = self.transcribe_image(image_path)
            results.append(result)
            
            # Save intermediate results every batch_size images
            if i % batch_size == 0:
                self._save_intermediate_results(results, i)
        
        return results
    
    def _save_intermediate_results(self, results: List[Dict], count: int):
        """Save intermediate results as JSON backup"""
        backup_path = self.output_dir / f"backup_results_{count}.json"
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Saved backup to {backup_path}")
    
    def compile_results(self, results: List[Dict], title: str = "Transcribed Content") -> str:
        """
        Compile all transcription results into a single formatted document
        
        Args:
            results: List of transcription results
            title: Title for the document
            
        Returns:
            Formatted text document
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        output = [
            f"# {title}",
            f"Transcribed on: {timestamp}",
            f"Total images processed: {len(results)}",
            f"Successful transcriptions: {sum(1 for r in results if r['success'])}",
            "",
            "---",
            ""
        ]
        
        for i, result in enumerate(results, 1):
            if result['success']:
                output.append(f"## Image {i}: {result['filename']}")
                output.append("")
                output.append(result['text'])
                output.append("")
                output.append("---")
                output.append("")
            else:
                output.append(f"## Image {i}: {result['filename']} [FAILED]")
                output.append(f"Error: {result['error']}")
                output.append("")
                output.append("---")
                output.append("")
        
        return "\n".join(output)
    
    def save_output(self, content: str, base_filename: str = "transcription"):
        """
        Save compiled content in multiple formats
        
        Args:
            content: The compiled text content
            base_filename: Base name for output files
        """
        # Save as TXT
        txt_path = self.output_dir / f"{base_filename}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nSaved text file: {txt_path}")
        
        # Save as Markdown
        md_path = self.output_dir / f"{base_filename}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved markdown file: {md_path}")
        
        return txt_path, md_path
    
    def process_directory(self, image_dir: str, output_filename: str = "transcription"):
        """
        Main method to process all images in a directory
        
        Args:
            image_dir: Directory containing images
            output_filename: Base name for output files
        """
        image_dir = Path(image_dir)
        
        # Find all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        image_paths = [
            p for p in sorted(image_dir.iterdir()) 
            if p.suffix.lower() in image_extensions
        ]
        
        if not image_paths:
            print(f"No images found in {image_dir}")
            return
        
        print(f"Found {len(image_paths)} images to process")
        print(f"Output directory: {self.output_dir}")
        print("\nStarting transcription...\n")
        
        # Transcribe all images
        results = self.transcribe_batch(image_paths)
        
        # Save full results as JSON
        json_path = self.output_dir / f"{output_filename}_full_results.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nSaved full results: {json_path}")
        
        # Compile and save readable output
        compiled_text = self.compile_results(results)
        txt_path, md_path = self.save_output(compiled_text, output_filename)
        
        # Print summary
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        print("\n" + "="*50)
        print("TRANSCRIPTION COMPLETE")
        print("="*50)
        print(f"Total images: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"\nReady for NotebookLM: {txt_path}")
        print("="*50)


def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Transcribe images using Claude API and compile for NotebookLM"
    )
    parser.add_argument(
        "image_dir",
        help="Directory containing images to transcribe"
    )
    parser.add_argument(
        "-o", "--output",
        default="transcription_output",
        help="Output directory (default: transcription_output)"
    )
    parser.add_argument(
        "-n", "--name",
        default="transcription",
        help="Base name for output files (default: transcription)"
    )
    parser.add_argument(
        "--api-key",
        help="Anthropic API key (optional if ANTHROPIC_API_KEY env var is set)"
    )
    
    args = parser.parse_args()
    
    try:
        transcriber = ImageTranscriber(
            api_key=args.api_key,
            output_dir=args.output
        )
        transcriber.process_directory(args.image_dir, args.name)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
