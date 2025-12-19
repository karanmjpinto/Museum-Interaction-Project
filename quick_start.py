#!/usr/bin/env python3
"""
Quick Start Script - Simplified interface for image transcription
Run this if you want a simple interactive setup
"""

import os
from pathlib import Path
from image_transcriber import ImageTranscriber

def main():
    print("=" * 60)
    print("IMAGE TRANSCRIBER FOR NOTEBOOKLM")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY not found in environment variables")
        api_key = input("Please enter your Anthropic API key: ").strip()
        if not api_key:
            print("❌ API key required. Exiting.")
            return 1
    else:
        print("✅ API key found")
    
    print()
    
    # Get image directory
    while True:
        image_dir = input("Enter the path to your images folder: ").strip()
        image_dir = Path(image_dir).expanduser()
        
        if image_dir.exists() and image_dir.is_dir():
            # Count images
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
            images = [p for p in image_dir.iterdir() if p.suffix.lower() in image_extensions]
            
            if images:
                print(f"✅ Found {len(images)} images")
                break
            else:
                print("❌ No images found in that directory")
        else:
            print("❌ Directory not found. Please try again.")
    
    print()
    
    # Get output preferences
    output_name = input("Output file name (default: transcription): ").strip() or "transcription"
    output_dir = input("Output directory (default: transcription_output): ").strip() or "transcription_output"
    
    print()
    print("=" * 60)
    print("READY TO PROCESS")
    print("=" * 60)
    print(f"Images to process: {len(images)}")
    print(f"Output directory: {output_dir}")
    print(f"Output filename: {output_name}")
    print(f"Estimated cost: ${len(images) * 0.003:.2f}")
    print(f"Estimated time: {len(images) * 7 // 60} minutes")
    print()
    
    proceed = input("Proceed? (yes/no): ").strip().lower()
    if proceed not in ['yes', 'y']:
        print("Cancelled.")
        return 0
    
    print()
    print("Starting transcription...")
    print()
    
    try:
        transcriber = ImageTranscriber(api_key=api_key, output_dir=output_dir)
        transcriber.process_directory(str(image_dir), output_name)
        
        print()
        print("✅ SUCCESS! Your transcription is ready.")
        print()
        print("Next steps:")
        print(f"1. Go to https://notebooklm.google.com/")
        print(f"2. Upload: {output_dir}/{output_name}.txt")
        print(f"3. Generate Audio Overview")
        print(f"4. Enjoy your podcast! 🎙️")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
