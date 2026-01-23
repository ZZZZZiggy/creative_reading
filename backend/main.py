from fastapi import FastAPI, UploadFile, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import uuid
import json
from pipeline import process_pdf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create data directories (always relative to repo root, not cwd)
BASE_DIR = Path(__file__).resolve().parent.parent / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
ARTIFACT_DIR = BASE_DIR / "artifacts"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

app.mount("/files", StaticFiles(directory=str(ARTIFACT_DIR)), name="files")

@app.post("/api/upload_pdf")
async def upload_pdf(file: UploadFile, background_tasks: BackgroundTasks):
    doc_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{doc_id}.pdf"

    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Process PDF in background
    background_tasks.add_task(process_pdf, file_path, doc_id)

    return {"message": "PDF uploaded successfully", "doc_id": doc_id}

@app.get("/api/get_pdf/{doc_id}")
async def get_pdf(doc_id: str):
    # Check for final processed content
    content_path = ARTIFACT_DIR / doc_id / "content.json"

    if not content_path.exists():
        return {"status": "processing"}

    try:
        with open(content_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
