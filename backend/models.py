from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class TranscribeResponse(BaseModel):
    transcript: str
    language_code: str
    is_demo: bool = False

class AnalyzeRequest(BaseModel):
    question_id: Optional[int] = None
    question_text: str
    expected_answer: str
    student_reasoning: str
    skill: Optional[str] = "Subtraction"
    language_code: Optional[str] = "en-IN"

class AnalyzeResponse(BaseModel):
    is_correct: bool
    detected_misconception: str
    misconception_category: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    explanation_of_student_reasoning: str
    teaching_strategy: str
    simple_reteaching_explanation: str
    follow_up_question: str
    is_demo: bool = False

class SpeakRequest(BaseModel):
    text: str
    language_code: Optional[str] = "en-IN"
    speaker: Optional[str] = "shubh"

class SpeakResponse(BaseModel):
    audio_base64: Optional[str] = None
    format: str = "wav"
    is_demo: bool = False
    message: Optional[str] = None

class SessionSaveRequest(BaseModel):
    student_id: int = 1
    question_id: int
    student_reasoning: str
    is_correct: bool
    detected_misconception: Optional[str] = None
    misconception_category: Optional[str] = None
    confidence_score: Optional[float] = 1.0
    simple_reteaching_explanation: Optional[str] = None

class QuestionModel(BaseModel):
    id: int
    grade: str
    skill: str
    question_text: str
    expected_answer: str
    hint: Optional[str] = None

class StudentProgressModel(BaseModel):
    student_name: str
    grade: str
    preferred_language: str
    total_questions: int
    correct_count: int
    accuracy_percentage: float
    skills_mastered: List[str]
    skills_needing_improvement: List[str]
    skill_breakdown: List[Dict[str, Any]]
    recent_sessions: List[Dict[str, Any]]
    common_misconceptions: List[Dict[str, Any]]
