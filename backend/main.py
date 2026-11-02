import os
import sys
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List

# Add parent and local path
sys.path.insert(0, os.path.dirname(__file__))

from models import (
    TranscribeResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    SpeakRequest,
    SpeakResponse,
    SessionSaveRequest,
    StudentProgressModel
)
from database import (
    get_questions,
    get_question_by_id,
    save_learning_session,
    get_student_progress,
    get_student_misconceptions
)
from taxonomy import TAXONOMY
import sarvam_service

app = FastAPI(
    title="Sunwai – AI Voice Tutor API",
    description="Mathematical Misconception Voice Tutor powered exclusively by Sarvam AI",
    version="1.0.0"
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

# -------------------------------------------------------------
# System & Status Endpoints
# -------------------------------------------------------------
@app.get("/api/status")
def get_status():
    """Returns current configuration status of Sarvam AI."""
    return sarvam_service.get_system_status()

@app.get("/api/taxonomy")
def get_taxonomy():
    """Returns the 6-skill misconception taxonomy."""
    return TAXONOMY

# -------------------------------------------------------------
# 1. Speech-to-Text Endpoint (Sarvam Saaras)
# -------------------------------------------------------------
@app.post("/api/transcribe", response_model=TranscribeResponse)
async def transcribe(
    audio_file: UploadFile = File(...),
    language_code: str = Form("en-IN")
):
    """
    Receives student's spoken audio and transcribes it via Sarvam Saaras API.
    """
    try:
        content = await audio_file.read()
        filename = audio_file.filename or "recording.wav"
        transcript, is_demo = sarvam_service.transcribe_audio(
            file_bytes=content,
            filename=filename,
            language_code=language_code
        )
        return TranscribeResponse(
            transcript=transcript,
            language_code=language_code,
            is_demo=is_demo
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

# -------------------------------------------------------------
# 2. Reasoning & Misconception Analysis Endpoint (Sarvam 105B)
# -------------------------------------------------------------
@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_reasoning(payload: AnalyzeRequest):
    """
    Evaluates student reasoning using Sarvam LLM, classifying misconceptions against taxonomy.
    """
    try:
        result = sarvam_service.analyze_reasoning(
            question_text=payload.question_text,
            expected_answer=payload.expected_answer,
            student_reasoning=payload.student_reasoning,
            skill=payload.skill or "Subtraction",
            language_code=payload.language_code or "en-IN"
        )
        return AnalyzeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# -------------------------------------------------------------
# 3. Text-to-Speech Endpoint (Sarvam Bulbul)
# -------------------------------------------------------------
@app.post("/api/speak", response_model=SpeakResponse)
async def speak(payload: SpeakRequest):
    """
    Synthesizes conversational explanation into natural voice using Sarvam Bulbul API.
    """
    try:
        audio_b64, is_demo, err_msg = sarvam_service.text_to_speech(
            text=payload.text,
            language_code=payload.language_code or "en-IN",
            speaker=payload.speaker or "shubh"
        )
        return SpeakResponse(
            audio_base64=audio_b64,
            format="wav",
            is_demo=is_demo,
            message=err_msg
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

# -------------------------------------------------------------
# 4. Learning Session & Persistence Endpoints
# -------------------------------------------------------------
@app.post("/api/session")
async def record_session(payload: SessionSaveRequest):
    """
    Persists student session, updates mastery percentages and misconception history.
    """
    try:
        session_id = save_learning_session(
            student_id=payload.student_id,
            question_id=payload.question_id,
            student_reasoning=payload.student_reasoning,
            is_correct=payload.is_correct,
            detected_misconception=payload.detected_misconception,
            misconception_category=payload.misconception_category,
            confidence_score=payload.confidence_score or 1.0,
            simple_reteaching_explanation=payload.simple_reteaching_explanation
        )
        return {"status": "success", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save session: {str(e)}")

@app.get("/api/questions")
def list_questions(skill: Optional[str] = None):
    """Retrieves maths questions for practice."""
    return get_questions(skill=skill)

@app.get("/api/student/progress", response_model=StudentProgressModel)
def student_progress(student_id: int = 1):
    """Retrieves student mastery, accuracy, and recent session records."""
    return get_student_progress(student_id)

@app.get("/api/student/misconceptions")
def student_misconceptions(student_id: int = 1):
    """Retrieves historical frequency of detected misconceptions for the student."""
    return get_student_misconceptions(student_id)

# -------------------------------------------------------------
# Static files & Frontend mount
# -------------------------------------------------------------
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
