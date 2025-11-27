import os
import shutil
import uuid
import asyncio
from typing import List, Dict, Optional
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Import our pipeline logic
from src.pipelines.fast import FastPipeline
from src.pipelines.balanced import BalancedPipeline
from src.pipelines.pro import ProPipeline
from src.cutting.smart_cut import SmartCutter
from src.processing.selector import PipelineSelector

app = FastAPI(title="ClipCut-MS API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store tasks in memory
tasks: Dict[str, Dict] = {}

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output_web"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ProcessRequest(BaseModel):
    video_filename: str
    pipeline: str = "auto"
    hf_token: Optional[str] = None

def run_pipeline_task(task_id: str, video_path: str, pipeline_type: str, hf_token: Optional[str]):
    try:
        tasks[task_id]["status"] = "processing"
        output_dir = os.path.join(OUTPUT_DIR, task_id)
        os.makedirs(output_dir, exist_ok=True)

        # Auto-selection
        if pipeline_type == "auto":
            selector = PipelineSelector()
            pipeline_type = selector.select(video_path)
            tasks[task_id]["pipeline_used"] = pipeline_type

        # Select Pipeline
        if pipeline_type == "fast":
            pipeline = FastPipeline()
        elif pipeline_type == "balanced":
            pipeline = BalancedPipeline(hf_token=hf_token)
        elif pipeline_type == "pro":
            pipeline = ProPipeline(hf_token=hf_token)
        else:
            raise ValueError(f"Unknown pipeline: {pipeline_type}")

        # Process
        tasks[task_id]["status"] = "analyzing"
        segments = pipeline.process(video_path, output_dir)
        
        # Calculate stats
        unique_speakers = set()
        for seg in segments:
            if "speaker" in seg:
                unique_speakers.add(seg["speaker"])
        
        tasks[task_id]["num_speakers"] = len(unique_speakers) if unique_speakers else 0
        tasks[task_id]["pipeline_used"] = pipeline_type # Ensure this is set even if not auto
        
        # Cut
        tasks[task_id]["status"] = "cutting"
        cutter = SmartCutter(output_dir)
        cutter.cut_segments(video_path, segments)

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["clips"] = [f for f in os.listdir(output_dir) if f.endswith(".mp4")]
        
    except Exception as e:
        print(f"Task {task_id} failed: {e}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

@app.post("/process")
async def start_process(request: ProcessRequest, background_tasks: BackgroundTasks):
    video_path = os.path.join(UPLOAD_DIR, request.video_filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "id": task_id,
        "status": "queued",
        "video": request.video_filename,
        "pipeline_requested": request.pipeline
    }

    background_tasks.add_task(
        run_pipeline_task, 
        task_id, 
        video_path, 
        request.pipeline, 
        request.hf_token
    )
    
    return {"task_id": task_id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.get("/clips/{task_id}")
async def get_clips(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    output_dir = os.path.join(OUTPUT_DIR, task_id)
    if not os.path.exists(output_dir):
        return {"clips": []}
        
    clips = [f for f in os.listdir(output_dir) if f.endswith(".mp4")]
    return {"clips": clips}

@app.get("/download/{task_id}/{clip_name}")
async def download_clip(task_id: str, clip_name: str):
    file_path = os.path.join(OUTPUT_DIR, task_id, clip_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Clip not found")
    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
