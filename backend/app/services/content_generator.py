"""Content generation service using Claude API"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import os
import json
from typing import List, Dict, Any
import anthropic
from backend.app.core.config import settings
from backend.app.api.models import ContentType

class ContentGenerator:
    """Generate educational content from transcriptions"""
    
    def __init__(self):
        """Initialize content generator"""
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def generate_flashcards(self, transcription_text: str, output_path: Path) -> str:
        """
        Generate flashcards from transcription
        
        Args:
            transcription_text: The transcribed text
            output_path: Path to save flashcards
            
        Returns:
            Path to generated flashcards file
        """
        prompt = f"""Based on the following museum exhibit transcription, create educational flashcards.

Each flashcard should have:
- A clear question on one side
- A concise, accurate answer on the other side
- Focus on key facts, dates, people, concepts, and important details

Format the output as JSON with this structure:
{{
  "flashcards": [
    {{
      "question": "Question text here",
      "answer": "Answer text here",
      "category": "Category (e.g., History, Art, Science)"
    }}
  ]
}}

Create 10-20 flashcards covering the most important information.

Transcription:
{transcription_text[:8000]}  # Limit to avoid token limits
"""
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        # Try to extract JSON from response
        try:
            # Look for JSON block
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            flashcards_data = json.loads(json_text)
            
            # Save as JSON
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(flashcards_data, f, indent=2, ensure_ascii=False)
            
            # Also save as readable text
            txt_path = output_path.with_suffix('.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("FLASHCARDS\n")
                f.write("=" * 50 + "\n\n")
                for i, card in enumerate(flashcards_data.get('flashcards', []), 1):
                    f.write(f"Card {i} - {card.get('category', 'General')}\n")
                    f.write(f"Q: {card.get('question', '')}\n")
                    f.write(f"A: {card.get('answer', '')}\n\n")
            
            return str(output_path)
        except Exception as e:
            # If JSON parsing fails, save raw response
            with open(output_path.with_suffix('.txt'), 'w', encoding='utf-8') as f:
                f.write(response_text)
            raise Exception(f"Failed to parse flashcards JSON: {e}")
    
    def generate_infographic_text(self, transcription_text: str, output_path: Path) -> str:
        """
        Generate infographic text content (structured summary)
        
        Args:
            transcription_text: The transcribed text
            output_path: Path to save infographic content
            
        Returns:
            Path to generated infographic file
        """
        prompt = f"""Based on the following museum exhibit transcription, create a structured infographic summary.

Format the content as a clear, visually-oriented summary with:
- Main title and subtitle
- Key statistics or numbers (if any)
- Important dates or timeline
- Key concepts or themes (3-5 bullet points)
- Notable facts or highlights
- Visual suggestions (what images/icons would work well)

Format as markdown with clear sections and bullet points.

Transcription:
{transcription_text[:8000]}
"""
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = message.content[0].text
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(output_path)
    
    def generate_video_script(self, transcription_text: str, output_path: Path) -> str:
        """
        Generate video script from transcription
        
        Args:
            transcription_text: The transcribed text
            output_path: Path to save video script
            
        Returns:
            Path to generated script file
        """
        prompt = f"""Based on the following museum exhibit transcription, create a video script suitable for text-to-speech or narration.

The script should:
- Be engaging and educational
- Be 2-3 minutes when read aloud (approximately 300-450 words)
- Have a clear introduction, main content, and conclusion
- Use conversational language suitable for general audiences
- Include natural pauses and emphasis markers [PAUSE] where appropriate
- Be formatted with clear scene descriptions and narration

Format:
[SCENE 1: Introduction]
NARRATOR: [Text here]

[SCENE 2: Main Content]
NARRATOR: [Text here]

[SCENE 3: Conclusion]
NARRATOR: [Text here]

Transcription:
{transcription_text[:8000]}
"""
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        script = message.content[0].text
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script)
        
        return str(output_path)
    
    def generate_podcast_format(self, transcription_text: str, output_path: Path) -> str:
        """
        Format transcription for podcast generation
        
        Args:
            transcription_text: The transcribed text
            output_path: Path to save podcast-formatted text
            
        Returns:
            Path to generated podcast file
        """
        prompt = f"""Based on the following museum exhibit transcription, format it as a podcast script.

The podcast script should:
- Have a clear introduction hook
- Be conversational and engaging
- Include natural transitions between topics
- Be suitable for audio narration (2-5 minutes)
- Include suggested music/sound effect cues in brackets
- Have clear speaker cues if multiple voices are used

Format:
[INTRO MUSIC]

HOST: [Introduction]

[TRANSITION MUSIC]

HOST: [Main content]

[OUTRO MUSIC]

Transcription:
{transcription_text[:8000]}
"""
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        podcast_script = message.content[0].text
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(podcast_script)
        
        return str(output_path)
    
    def generate_content(self, transcription_text: str, content_types: List[ContentType], output_dir: Path) -> Dict[str, str]:
        """
        Generate multiple content types
        
        Args:
            transcription_text: The transcribed text
            content_types: List of content types to generate
            output_dir: Directory to save generated content
            
        Returns:
            Dictionary mapping content type to file path
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = {}
        
        for content_type in content_types:
            if content_type == ContentType.FLASHCARDS:
                file_path = output_dir / "flashcards.json"
                generated_files["flashcards"] = self.generate_flashcards(transcription_text, file_path)
            elif content_type == ContentType.INFOGRAPHICS:
                file_path = output_dir / "infographic.md"
                generated_files["infographics"] = self.generate_infographic_text(transcription_text, file_path)
            elif content_type == ContentType.VIDEO_SCRIPT:
                file_path = output_dir / "video_script.txt"
                generated_files["video_script"] = self.generate_video_script(transcription_text, file_path)
            elif content_type == ContentType.PODCAST:
                file_path = output_dir / "podcast_script.txt"
                generated_files["podcast"] = self.generate_podcast_format(transcription_text, file_path)
        
        return generated_files

