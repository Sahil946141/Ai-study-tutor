import requests

# Base URL for the backend FastAPI service.
# Update this if your backend runs on a different host/port.
BASE_URL = "http://localhost:8000"


def _handle_response(response: requests.Response):
    try:
        response.raise_for_status()
    except requests.HTTPError:
        # Try to extract a friendly error message from FastAPI
        try:
            payload = response.json()
            detail = payload.get("detail") or payload.get("error")
            message = detail if detail else response.text
        except Exception:
            message = response.text
        return {"error": f"{response.status_code}: {message}"}

    try:
        return response.json()
    except ValueError:
        return {"error": "Invalid JSON response from server."}


def get_health():
    """Check backend health."""
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


def explain_topic(topic: str, grade_level: str):
    """Request an explanation for a topic from the backend."""
    try:
        resp = requests.post(
            f"{BASE_URL}/explain",
            json={"topic": topic, "grade_level": grade_level},
            timeout=30,
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


def generate_quiz(topic: str, difficulty: str, num_questions: int):
    """Request a new quiz from the backend."""
    try:
        resp = requests.post(
            f"{BASE_URL}/quiz/generate",
            json={
                "topic": topic,
                "difficulty": difficulty,
                "num_questions": num_questions,
            },
            timeout=60,
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


def submit_quiz(user_id: str, quiz_id: str, answers: dict):
    """Submit quiz answers to the backend."""
    try:
        resp = requests.post(
            f"{BASE_URL}/quiz/submit",
            json={"user_id": user_id, "quiz_id": quiz_id, "answers": answers},
            timeout=60,
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


def get_progress(user_id: str):
    """Fetch progress data for a user."""
    try:
        resp = requests.get(f"{BASE_URL}/progress/{user_id}", timeout=30)
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}
