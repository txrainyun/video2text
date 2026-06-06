
"""
Video2Text - 简化版本，用于测试
不会自动加载 Whisper 模型，避免启动问题
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
    description="本地音视频转文字工具",
    version="1.0.0"
)

# 配置
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
TASKS_FILE = Path("tasks.json")

# 全局变量
model_manager = None
transcription_service = None
tasks: Dict[str, dict] = {}

# 辅助函数
def save_tasks():
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def load_tasks():
    global tasks
    if TASKS_FILE.exists():
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            tasks = json.load(f)

def init_model():
    """延迟加载模型"""
    global model_manager, transcription_service
    try:
        from whisper_model import WhisperModel
        from transcription import TranscriptionService
        model_manager = WhisperModel()
        transcription_service = TranscriptionService(None)
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Model loading failed: {e}")
        return False

def ensure_model_loaded():
    """确保模型已加载，返回 (success, error_message)"""
    global model_manager, transcription_service
    
    # 初始化管理器和服务
    if model_manager is None or transcription_service is None:
        if not init_model():
            return False, "模型初始化失败"
    
    # 加载实际模型
    if transcription_service.model is None:
        try:
            print("正在加载 Whisper 模型，首次使用需要下载（约140MB）...")
            model_manager.load_model()
            transcription_service.model = model_manager.model
            print("模型加载完成！")
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"模型加载失败: {str(e)}"
    
    return True, None

@app.on_event("startup")
async def startup():
    load_tasks()
    print("=" * 50)
    print("Video2Text 服务已启动")
    print("=" * 50)

@app.get("/")
async def root():
    return FileResponse("public/index.html")

app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/health")
async def health():
    model_ok = model_manager is not None and model_manager.model is not None
    return {
        "status": "ok", 
        "model_loaded": model_ok,
        "message": "服务运行正常"
    }

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
        "device": info["device"]
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
    # 确保模型已加载
    success, error = ensure_model_loaded()
    if not success:
        raise HTTPException(status_code=500, detail=error)
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 保存文件
    file_path = UPLOAD_DIR / f"{task_id}_{file.filename}"
    
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    
    # 创建任务
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
    
    # 启动转录任务
    asyncio.create_task(process_transcription(task_id))
    
    return {
        "file_id": task_id,
        "filename": file.filename,
        "status": "queued"
    }

async def process_transcription(task_id: str):
    """处理转录任务"""
    task = tasks[task_id]
    
    try:
        # 确保模型已加载
        success, error = ensure_model_loaded()
        if not success:
            raise Exception(error)
        
        # 更新状态
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 10
        save_tasks()
        
        # 执行转录
        result = await transcription_service.transcribe(task["file_path"])
        
        # 保存结果
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["result"] = result
        save_tasks()
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
        save_tasks()

@app.get("/status/{file_id}")
async def get_status(file_id: str):
    if file_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
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
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[file_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="任务未完成")
    
    return task["result"]

@app.get("/export/{file_id}")
async def export_file(
    file_id: str,
    format: str = Query("txt", pattern="^(txt|md|srt)$"),
    include_timestamps: bool = Query(True)
):
    if file_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[file_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="任务未完成")
    
    # 确保转录服务已初始化
    success, error = ensure_model_loaded()
    if not success:
        raise HTTPException(status_code=500, detail=error)
    
    result = task["result"]
    segments = result["segments"]
    filename = Path(task["filename"]).stem
    
    if format == "txt":
        content = transcription_service.format_txt(segments, include_timestamps)
        return JSONResponse({
            "content": content,
            "filename": f"{filename}.txt"
        })
    
    elif format == "md":
        content = transcription_service.format_markdown(segments, filename)
        return JSONResponse({
            "content": content,
            "filename": f"{filename}.md"
        })
    
    elif format == "srt":
        content = transcription_service.format_srt(segments)
        return JSONResponse({
            "content": content,
            "filename": f"{filename}.srt"
        })

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
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[file_id]
    
    # 删除文件
    if os.path.exists(task["file_path"]):
        os.remove(task["file_path"])
    
    # 删除任务
    del tasks[file_id]
    save_tasks()
    
    return {"status": "deleted"}

if __name__ == "__main__":
    print("=" * 50)
    print("启动 Video2Text 服务...")
    print("访问: http://127.0.0.1:8000")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
