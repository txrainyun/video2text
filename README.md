
# Video2Text - Local Audio/Video to Text Tool

A local web application to transcribe audio/video files to text, with optional subtitle export.

## Quick Start (Windows)

### Step 1: Install Dependencies
Double-click `install.bat`

### Step 2: Start the Application
Double-click `start.bat`

### Step 3: Open in Browser
Visit: http://127.0.0.1:8000

---

## Available Versions

| File | Description | Dependencies |
|------|-------------|----------------|
| **app_minimal.py** | **Recommended** - Simulated for testing | requirements_simple.txt |
| app_simple.py | Full version (Whisper) | requirements.txt |
| app.py | Original version | requirements.txt |

---

## Features

- Upload video/audio files
- Queue processing
- Full text display
- Multiple export formats (TXT/Markdown/SRT)

## System Requirements

- Python 3.8+
- Memory: 8GB+ recommended
- Disk: 3GB+ for Whisper models

## Installation Steps

### 1. Install Python Dependencies

```bash
python -m pip install -r requirements_simple.txt
```

### 2. Start Application

```bash
python app_minimal.py
```

## Usage

1. Upload files
2. View results
3. Export transcripts

---

## Project Structure

```
video2text/
├── app_minimal.py       # Minimal version (simulated)
├── app_simple.py      # Full version
├── app.py             # Original
├── requirements_simple.txt # Minimal dependencies
├── requirements.txt       # Full dependencies
├── public/            # Frontend files
├── public/index.html
├── public/style.css
└── public/app.js
├── uploads/           # Uploaded files
├── start.bat         # Start script
└── install.bat       # Install script
```

---

## Notes

- Current version simulates transcription for testing purposes. Real Whisper integration will be added later.
