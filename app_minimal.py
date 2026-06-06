
"""
Video2Text - Minimal version (no Whisper)
用于测试基本的web服务
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import uvicorn
import uuid
import json
import os
import asyncio
from typing import Dict, Optional

app = FastAPI(
    title="Video2Text API",
    description="Local audio/video to text tool",
    version="1.0.0"
)

# Configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
TASKS_FILE = Path("tasks.json")

# Global variables
tasks: Dict[str, dict] = {}

# Helper functions
def save_tasks():
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def load_tasks():
    global tasks
    if TASKS_FILE.exists():
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            tasks = json.load(f)

@app.on_event("startup")
async def startup():
    load_tasks()
    print("=" * 50)
    print("Video2Text Service Started!")
    print("=" * 50)

@app.get("/")
async def root():
    return FileResponse("public/index.html")

app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "message": "Service running"
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Save file
    file_path = UPLOAD_DIR / f"{task_id}_{file.filename}"
    
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create task (simulate processing)
    tasks[task_id] = {
        "id": task_id,
        "filename": file.filename,
        "file_path": str(file_path),
        "status": "queued",
        "progress": 0,
        "result": None,
        "error": None
    }
    save_tasks()
    
    # Simulate processing
    asyncio.create_task(simulate_processing(task_id))
    
    return {
        "file_id": task_id,
        "filename": file.filename,
        "status": "queued"
    }

async def simulate_processing(task_id: str):
    """Simulate processing task"""
    task = tasks[task_id]
    
    try:
        # Update status
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 10
        save_tasks()
        
        # Simulate work
        await asyncio.sleep(2)
        tasks[task_id]["progress"] = 50
        save_tasks()
        
        await asyncio.sleep(2)
        tasks[task_id]["progress"] = 100
        save_tasks()
        
        # Mock result
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = {
            "text": "This is a sample transcription result.\nThis is line 2 of the result.",
            "segments": [
                {"start": 0.0, "end": 2.0, "text": "This is a sample transcription result."},
                {"start": 2.0, "end": 4.0, "text": "This is line 2 of the result."}
            ],
            "language": "en",
            "duration": 4.0
        }
        save_tasks()
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
        save_tasks()

@app.get("/status/{file_id}")
async def get_status(file_id: str):
    if file_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[file_id]
    return {
        "file_id": file_id,
        "status": task["status"],
        "progress": task["progress"],
        "error": task.get("error")
    }

@app.get("/result/{file_id}")
async def get_result(file_id: str):
    if file_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[file_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    return task["result"]

@app.get("/tasks")
async def list_tasks():
    return [
        {
            "id": t["id"],
            "filename": t["filename"],
            "status": t["status"],
            "progress": t["progress"]
        }
        for t in tasks.values()
    ]

@app.delete("/task/{file_id}")
async def delete_task(file_id: str):
    if file_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[file_id]
    
    # Delete file
    if os.path.exists(task["file_path"]):
        os.remove(task["file_path"])
    
    # Delete task
    del tasks[file_id]
    save_tasks()
    
    return {"status": "deleted"}

@app.get("/export/{file_id}")
async def export_file(
    file_id: str,
    format: str = Query("txt", regex="^(txt|md|srt)$"),
    include_timestamps: bool = Query(True)
):
    if file_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[file_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    result = task["result"]
    segments = result["segments"]
    filename = Path(task["filename"]).stem
    
    content = ""
    
    if format == "txt":
        for seg in segments:
            if include_timestamps:
                time_str = format_time(seg["start"])
                content += f"[{time_str}] {seg['text']}\n\n"
            else:
                content += f"{seg['text']}\n\n"
    elif format == "md":
        content = f"# {filename}\n\n"
        for seg in segments:
            time_str = format_time(seg["start"])
            content += f"> [{time_str}]\n>\n> {seg['text']}\n\n---\n\n"
    elif format == "srt":
        for i, seg in enumerate(segments, 1):
            start = format_srt_time(seg["start"])
            end = format_srt_time(seg["end"])
            content += f"{i}\n{start} --> {end}\n{seg['text']}\n\n"
    
    return JSONResponse({
        "content": content,
        "filename": f"{filename}.{format}"
    })

def format_time(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def format_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

if __name__ == "__main__":
    print("=" * 50)
    print("Starting Video2Text Service (Minimal)...")
    print("Visit: http://127.0.0.1:8000")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
