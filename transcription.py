from pathlib import Path
from typing import Optional
import whisper
import uuid

class TranscriptionService:
    def __init__(self, model):
        self.model = model
    
    async def transcribe(self, file_path: str, language: Optional[str] = None):
        result = self.model.transcribe(
            file_path,
            language=language,
            verbose=False
        )
        return {
            "text": result["text"],
            "segments": result["segments"],
            "language": result.get("language", "unknown")
        }
    
    def format_srt(self, segments: list) -> str:
        srt_content = ""
        for i, segment in enumerate(segments, 1):
            start = self._format_timestamp(segment["start"])
            end = self._format_timestamp(segment["end"])
            text = segment["text"].strip()
            srt_content += f"{i}\n{start} --> {end}\n{text}\n\n"
        return srt_content
    
    def _format_timestamp(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
