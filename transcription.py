from pathlib import Path
from typing import Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import subprocess
import os

class TranscriptionService:
    def __init__(self, model):
        self.model = model
        self.executor = ThreadPoolExecutor(max_workers=2)

    def _extract_audio(self, video_path: str) -> str:
        """从视频中提取音频"""
        audio_path = video_path.rsplit('.', 1)[0] + '_audio.wav'

        # 检查是否已经是音频文件
        ext = Path(video_path).suffix.lower()
        if ext in ['.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg']:
            return video_path

        # 使用ffmpeg提取音频
        try:
            subprocess.run([
                'ffmpeg', '-i', video_path,
                '-vn', '-acodec', 'pcm_s16le',
                '-ar', '16000', '-ac', '1',
                '-y', audio_path
            ], check=True, capture_output=True)
            return audio_path
        except subprocess.CalledProcessError:
            # 如果ffmpeg不可用，直接返回原文件
            return video_path

    async def transcribe(
        self,
        file_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
        progress_callback=None
    ) -> Dict[str, Any]:
        """异步转录 - 使用 faster_whisper API"""
        # 提取音频
        audio_path = self._extract_audio(file_path)

        # 在线程池中执行转录
        loop = asyncio.get_event_loop()

        def do_transcribe():
            segments_iter, info = self.model.transcribe(
                audio_path,
                language=language,
                task=task,
                beam_size=5,
                vad_filter=True,
            )

            segments_list = []
            full_text = ""
            for segment in segments_iter:
                segments_list.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                })
                full_text += segment.text

            return {
                "text": full_text.strip(),
                "segments": segments_list,
                "language": info.language,
                "duration": info.duration,
            }

        result = await loop.run_in_executor(self.executor, do_transcribe)

        # 清理临时音频文件
        if audio_path != file_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass

        return result

    def format_srt(self, segments: list) -> str:
        """生成SRT字幕文件"""
        srt_content = ""
        for i, segment in enumerate(segments, 1):
            start = self._format_timestamp(segment["start"])
            end = self._format_timestamp(segment["end"])
            text = segment["text"].strip()
            srt_content += f"{i}\n{start} --> {end}\n{text}\n\n"
        return srt_content

    def format_txt(self, segments: list, include_timestamps: bool = True) -> str:
        """生成TXT文本"""
        if include_timestamps:
            content = ""
            for segment in segments:
                start = self._format_timestamp(segment["start"])
                text = segment["text"].strip()
                content += f"[{start}] {text}\n\n"
            return content
        else:
            return "".join(seg["text"].strip() + "\n\n" for seg in segments)

    def format_markdown(self, segments: list, title: str = "转录结果") -> str:
        """生成Markdown文档"""
        md = f"# {title}\n\n"
        for segment in segments:
            start = self._format_timestamp(segment["start"])
            text = segment["text"].strip()
            md += f"> [{start}]\n>\n> {text}\n\n---\n\n"
        return md

    def _format_timestamp(self, seconds: float) -> str:
        """格式化时间戳为 HH:MM:SS,mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
