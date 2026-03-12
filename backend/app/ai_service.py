import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)

def generate_explanation(topic: str, grade_level: str):
    prompt = PromptTemplate(
        input_variables=["topic", "grade_level"],
        template="""
You are a helpful AI tutor for students.

Explain the topic "{topic}" in a simple and engaging way for a {grade_level} student.

Return only valid JSON in this format:
{{
  "topic": "{topic}",
  "explanation": "simple explanation here",
  "example": "one real life example here",
  "key_points": [
    "point 1",
    "point 2",
    "point 3"
  ]
}}

Rules:
- Keep the explanation easy to understand
- Do not use markdown
- Do not add any text outside JSON
"""
    )

    chain = prompt | llm
    response = chain.invoke({
        "topic": topic,
        "grade_level": grade_level
    })

    content = response.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise Exception("Failed to parse explanation JSON from LLM response.")


def generate_quiz(topic: str, difficulty: str, num_questions: int):
    prompt = PromptTemplate(
        input_variables=["topic", "difficulty", "num_questions"],
        template="""
You are an AI quiz generator for students.

Generate exactly {num_questions} multiple choice questions on the topic "{topic}".
Difficulty level: {difficulty}

Return only valid JSON in this format:
{{
  "topic": "{topic}",
  "difficulty": "{difficulty}",
  "questions": [
    {{
      "question_id": 1,
      "question": "question text",
      "options": ["option 1", "option 2", "option 3", "option 4"],
      "correct_answer": "one of the options exactly",
      "explanation": "short explanation"
    }}
  ]
}}

Rules:
- Generate exactly {num_questions} questions
- Each question must have exactly 4 options
- correct_answer must match one of the options exactly
- Keep questions student-friendly
- Do not use markdown
- Do not add any text outside JSON
"""
    )

    chain = prompt | llm
    response = chain.invoke({
        "topic": topic,
        "difficulty": difficulty,
        "num_questions": num_questions
    })

    content = response.content.strip()

    try:
        quiz_data = json.loads(content)
    except json.JSONDecodeError:
        raise Exception("Failed to parse quiz JSON from LLM response.")

    if "questions" not in quiz_data or not isinstance(quiz_data["questions"], list):
        raise Exception("Invalid quiz format returned by LLM.")

    if len(quiz_data["questions"]) != num_questions:
        raise Exception("LLM did not return the requested number of questions.")

    for i, q in enumerate(quiz_data["questions"], start=1):
        if "question_id" not in q:
            q["question_id"] = i

        if "question" not in q or "options" not in q or "correct_answer" not in q:
            raise Exception("A quiz question is missing required fields.")

        if not isinstance(q["options"], list) or len(q["options"]) != 4:
            raise Exception("Each quiz question must have exactly 4 options.")

        if q["correct_answer"] not in q["options"]:
            raise Exception("correct_answer must match one of the options exactly.")

    return quiz_data