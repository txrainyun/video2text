"""
Video2Text - ??????????
??? Whisper ???????
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import uvicorn
import uuid
import json
import os
import asyncio
from typing import Dict

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
TASKS_FILE = Path("tasks.json")

model_manager = None
transcription_service = None
tasks: Dict[str, dict] = {}
_pending_tasks: set = set()


def save_tasks():
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def load_tasks():
    global tasks
    if TASKS_FILE.exists():
        with open(TASKS_FILE, "r", encoding="utf-8-sig") as f:
            tasks = json.load(f)


def init_model():
    global model_manager, transcription_service
    try:
        from whisper_model import WhisperModel
        from transcription import TranscriptionService
        model_manager = WhisperModel()
        transcription_service = TranscriptionService(None)
        model_manager.load_model()
        transcription_service.model = model_manager.model
        print("模型加载成功！")
        return True
    except Exception as e:
        print(f"模型加载失败: {e}")
        return False


def ensure_model_loaded():
    global model_manager, transcription_service
    if model_manager is None or transcription_service is None:
        if not init_model():
            return False, "???????"
    if transcription_service.model is None:
        try:
            model_manager.load_model()
            transcription_service.model = model_manager.model
        except Exception as e:
            return False, "????????????"
    return True, None


@asynccontextmanager
async def lifespan(app):
    load_tasks()
    print("Video2Text ?????")
    yield
    print("\n?????????????...")
    for fpath in UPLOAD_DIR.iterdir():
        if fpath.suffix == ".wav" and "_" in fpath.stem:
            try:
                fpath.unlink()
            except OSError:
                pass
    print("?????")


app = FastAPI(
    lifespan=lifespan,
    title="Video2Text API",
    description="??????????",
    version="1.1.0"
)


@app.get("/")
async def root():
    return FileResponse("public/index.html")


@app.get("/health")
async def health():
    model_ok = model_manager is not None and model_manager.model is not None
    return {"status": "ok", "model_loaded": model_ok, "version": "1.1.0"}


@app.get("/models")
async def get_models():
    success, error = ensure_model_loaded()
    if not success:
        raise HTTPException(status_code=500, detail=error)
    info = model_manager.get_model_info()
    return {
        "current_model": info["name"],
        "available_models": info["available"],
        "model_size": info["size"],
        "device": info["device"],
    }


@app.post("/model")
async def switch_model(model_name: str = Query(...)):
    success, error = ensure_model_loaded()
    if not success:
        raise HTTPException(status_code=500, detail=error)
    try:
        model_manager.switch_model(model_name)
        transcription_service.model = model_manager.model
        return {"status": "success", "new_model": model_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 不在上传时阻塞式加载模型，避免大型模型加载导致上传接口失败。
    # 模型加载将在后台任务处理中进行（process_transcription）。
    task_id = str(uuid.uuid4())
    safe_name = file.filename or "unknown"
    file_path = UPLOAD_DIR / f"{task_id}_{safe_name}"

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")

    tasks[task_id] = {
        "id": task_id,
        "filename": safe_name,
        "file_path": str(file_path),
        "status": "queued",
        "progress": 0,
        "result": None,
        "error": None,
        "language": None,
        "duration": 0,
    }
    save_tasks()

    coro = asyncio.create_task(process_transcription(task_id))
    _pending_tasks.add(coro)
    coro.add_done_callback(_pending_tasks.discard)

    return {"file_id": task_id, "filename": safe_name, "status": "queued"}


async def process_transcription(task_id: str):
    task = tasks[task_id]
    try:
        success, error = ensure_model_loaded()
        if not success:
            raise Exception(error)
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 10
        save_tasks()
        result = await transcription_service.transcribe(task["file_path"])
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["result"] = result
        tasks[task_id]["language"] = result.get("language")
        tasks[task_id]["duration"] = result.get("duration", 0)
        save_tasks()
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
        save_tasks()


@app.get("/status/{file_id}")
async def get_status(file_id: str):
    if file_id not in tasks:
        raise HTTPException(status_code=404, detail="?????")
    t = tasks[file_id]
    return {
        "file_id": file_id,
        "status": t["status"],
        "progress": t["progress"],
        "error": t.get("error"),
        "language": t.get("language"),
        "duration": t.get("duration"),
    }


@app.get("/result/{file_id}")
async def get_result(file_id: str):
    if file_id not in tasks:
        raise HTTPException(status_code=404, detail="?????")
    t = tasks[file_id]
    if t["status"] != "completed":
        raise HTTPException(status_code=400, detail="??????")
    return t["result"]


@app.get("/export/{file_id}")
async def export_file(
    file_id: str,
    fmt: str = Query("txt", alias="format", pattern="^(txt|md|srt)$"),
    include_timestamps: bool = Query(True),
):
    if file_id not in tasks:
        raise HTTPException(status_code=404, detail="?????")
    t = tasks[file_id]
    if t["status"] != "completed":
        raise HTTPException(status_code=400, detail="??????")

    segments = t["result"]["segments"]
    stem = Path(t["filename"]).stem

    lines = []
    if fmt == "txt":
        for seg in segments:
            ts = _fmt_srt(seg["start"]) if include_timestamps else ""
            prefix = f"[{ts}] " if include_timestamps else ""
            lines.append(f"{prefix}{seg['text'].strip()}\n")
        content = "\n".join(lines)
        name = f"{stem}.txt"
    elif fmt == "md":
        lines.append(f"# {stem}\n")
        for seg in segments:
            ts = _fmt_srt(seg["start"])
            lines.append(f"> [{ts}]\n>\n> {seg['text'].strip()}\n\n---\n")
        content = "\n".join(lines)
        name = f"{stem}.md"
    else:
        for i, seg in enumerate(segments, 1):
            s = _fmt_srt(seg["start"])
            e = _fmt_srt(seg["end"])
            lines.append(f"{i}\n{s} --> {e}\n{seg['text'].strip()}\n")
        content = "\n".join(lines)
        name = f"{stem}.srt"

    return JSONResponse({"content": content, "filename": name})


def _fmt_srt(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


@app.get("/tasks")
async def list_tasks():
    return [
        {
            "id": t["id"],
            "filename": t["filename"],
            "status": t["status"],
            "progress": t["progress"],
            "language": t.get("language"),
            "duration": t.get("duration"),
        }
        for t in tasks.values()
    ]


@app.delete("/task/{file_id}")
async def delete_task(file_id: str):
    if file_id not in tasks:
        raise HTTPException(status_code=404, detail="?????")
    t = tasks[file_id]
    fp = t.get("file_path")
    if fp and os.path.exists(fp):
        try:
            os.remove(fp)
        except OSError:
            pass
    del tasks[file_id]
    save_tasks()
    return {"status": "deleted"}


app.mount("/public", StaticFiles(directory="public"), name="public")


if __name__ == "__main__":
    print("=" * 50)
    print("Video2Text v1.1.0")
    print("??: http://127.0.0.1:8000")
    print("????????")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
