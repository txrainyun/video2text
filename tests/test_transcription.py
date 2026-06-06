import pytest
import tempfile
import wave
import struct
import hashlib
from transcription import TranscriptionService

def test_format_timestamp():
    service = TranscriptionService(None)
    assert service._format_timestamp(0.0) == "00:00:00,000"
    assert service._format_timestamp(3.5) == "00:00:03,500"
    assert service._format_timestamp(65.25) == "00:01:05,250"

def test_format_srt():
    service = TranscriptionService(None)
    segments = [
        {"start": 0.0, "end": 3.5, "text": "测试文字一"},
        {"start": 3.5, "end": 7.2, "text": "测试文字二"}
    ]
    srt = service.format_srt(segments)
    assert "1\n00:00:00,000 --> 00:00:03,500\n测试文字一" in srt
    assert "2\n00:00:03,500 --> 00:00:07,200\n测试文字二" in srt

def test_format_txt_with_timestamps():
    service = TranscriptionService(None)
    segments = [
        {"start": 0.0, "end": 3.5, "text": "第一段"},
        {"start": 3.5, "end": 7.2, "text": "第二段"}
    ]
    txt = service.format_txt(segments, include_timestamps=True)
    assert "[00:00:00,000] 第一段" in txt
    assert "[00:00:03,500] 第二段" in txt

def test_format_txt_without_timestamps():
    service = TranscriptionService(None)
    segments = [
        {"start": 0.0, "end": 3.5, "text": "第一段"},
        {"start": 3.5, "end": 7.2, "text": "第二段"}
    ]
    txt = service.format_txt(segments, include_timestamps=False)
    assert "第一段" in txt
    assert "第二段" in txt
    assert "[00:00" not in txt

def test_format_markdown():
    service = TranscriptionService(None)
    segments = [
        {"start": 0.0, "end": 3.5, "text": "测试内容"}
    ]
    md = service.format_markdown(segments, "测试标题")
    assert "# 测试标题" in md
    assert "00:00:00,000" in md
    assert "测试内容" in md
