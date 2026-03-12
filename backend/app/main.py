from fastapi import FastAPI, HTTPException
from app.db import get_connection
from app.schemas import ExplainRequest, QuizGenerateRequest, QuizSubmitRequest
from app.ai_service import generate_explanation, generate_quiz
from app.quiz_service import save_quiz, evaluate_quiz
from app.progress_service import get_user_progress

app = FastAPI(
    title="AI Study Companion API",
    description="Backend API for Gamified AI Study Companion",
    version="1.0"
)


@app.get("/")
def root():
    return {"message": "AI Study Companion API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/test-db")
def test_database():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return {
            "database": "connected",
            "version": db_version
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain")
def explain_concept(request: ExplainRequest):
    try:
        result = generate_explanation(
            topic=request.topic,
            grade_level=request.grade_level
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/quiz/generate")
def generate_quiz_endpoint(request: QuizGenerateRequest):
    try:
        topic = request.topic.strip().title()

        quiz_data = generate_quiz(
            topic=topic,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
        )

        quiz_id, saved_questions = save_quiz(
            topic=topic,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
            questions=quiz_data["questions"],
        )

        return {
            "quiz_id": quiz_id,
            "topic": topic,
            "difficulty": request.difficulty,
            "questions": saved_questions,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/quiz/submit")
def submit_quiz(request: QuizSubmitRequest):
    try:
        result = evaluate_quiz(
            user_id=request.user_id,
            quiz_id=request.quiz_id,
            answers=request.answers
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/progress/{user_id}")
def progress(user_id: str):
    try:
        progress_data = get_user_progress(user_id)
        return progress_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))