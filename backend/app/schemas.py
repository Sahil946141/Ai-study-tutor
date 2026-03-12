from pydantic import BaseModel
from typing import Dict


class ExplainRequest(BaseModel):
    topic: str
    grade_level: str


class QuizGenerateRequest(BaseModel):
    topic: str
    difficulty: str
    num_questions: int


class QuizSubmitRequest(BaseModel):
    user_id: str
    quiz_id: str
    answers: Dict[str, str]