import json
from app.db import get_connection


def create_user_if_not_exists(user_id: str, name: str = "Student"):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            cursor.execute(
                """
                INSERT INTO users (id, name, total_points, level)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, name, 0, 1)
            )
            conn.commit()

    finally:
        cursor.close()
        conn.close()


def save_quiz(topic: str, difficulty: str, num_questions: int, questions: list):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
        """
        INSERT INTO quizzes (topic, difficulty, num_questions)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (topic, difficulty, num_questions)
    )
        quiz_id = cursor.fetchone()[0]

        saved_questions = []
        for q in questions:
            cursor.execute(
                """
                INSERT INTO quiz_questions (quiz_id, question, options, correct_answer, explanation)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    quiz_id,
                    q["question"],
                    json.dumps(q["options"]),
                    q["correct_answer"],
                    q["explanation"],
                )
            )
            question_id = cursor.fetchone()[0]
            saved_questions.append(
                {
                    "question_id": str(question_id),
                    "question": q["question"],
                    "options": q["options"],
                }
            )

        conn.commit()
        return quiz_id, saved_questions

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def calculate_points(score: int, total: int):
    points = score * 10
    if score == total and total > 0:
        points += 20
    return points


def calculate_level(total_points: int):
    return (total_points // 50) + 1


def award_badge_if_not_exists(cursor, user_id: str, badge_name: str, badges_awarded: list):
    cursor.execute(
        """
        SELECT id FROM badges
        WHERE user_id = %s AND badge_name = %s
        """,
        (user_id, badge_name)
    )
    existing_badge = cursor.fetchone()

    if not existing_badge:
        cursor.execute(
            """
            INSERT INTO badges (user_id, badge_name)
            VALUES (%s, %s)
            """,
            (user_id, badge_name)
        )
        badges_awarded.append(badge_name)


def evaluate_quiz(user_id: str, quiz_id: int, answers: dict):
    create_user_if_not_exists(user_id)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, question, options, correct_answer, explanation
            FROM quiz_questions
            WHERE quiz_id = %s
            ORDER BY id
            """,
            (quiz_id,)
        )
        questions = cursor.fetchall()

        if not questions:
            raise Exception("Quiz not found or has no questions.")

        score = 0
        total = len(questions)
        results = []

        for q in questions:
            question_id = str(q[0])
            question_text = q[1]
            options = q[2]
            correct_answer = q[3]
            explanation = q[4]

            user_answer = answers.get(question_id)

            is_correct = user_answer == correct_answer
            if is_correct:
                score += 1

            results.append({
                "question_id": question_id,
                "question": question_text,
                "your_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": explanation
            })

        points_earned = calculate_points(score, total)

        cursor.execute(
            """
            SELECT total_points FROM users
            WHERE id = %s
            """,
            (user_id,)
        )
        user_row = cursor.fetchone()
        current_points = user_row[0] if user_row else 0

        new_total_points = current_points + points_earned
        new_level = calculate_level(new_total_points)

        cursor.execute(
            """
            UPDATE users
            SET total_points = %s, level = %s
            WHERE id = %s
            """,
            (new_total_points, new_level, user_id)
        )

        cursor.execute(
            """
            INSERT INTO quiz_attempts (user_id, quiz_id, score, total, points_earned)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (user_id, quiz_id, score, total, points_earned)
        )
        attempt_id = cursor.fetchone()[0]

        for result in results:
            cursor.execute(
                """
                INSERT INTO attempt_answers (attempt_id, question_id, user_answer, is_correct)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    attempt_id,
                    int(result["question_id"]),
                    result["your_answer"],
                    result["is_correct"]
                )
            )

        badges_awarded = []

        award_badge_if_not_exists(cursor, user_id, "First Quiz Completed", badges_awarded)

        if score == total and total > 0:
            award_badge_if_not_exists(cursor, user_id, "Perfect Score", badges_awarded)

        cursor.execute(
            """
            SELECT COUNT(*) FROM quiz_attempts
            WHERE user_id = %s
            """,
            (user_id,)
        )
        attempts_count = cursor.fetchone()[0]

        if attempts_count >= 3:
            award_badge_if_not_exists(cursor, user_id, "Quiz Explorer", badges_awarded)

        conn.commit()

        return {
            "user_id": user_id,
            "quiz_id": quiz_id,
            "score": score,
            "total": total,
            "points_earned": points_earned,
            "new_total_points": new_total_points,
            "new_level": new_level,
            "badges_awarded": badges_awarded,
            "results": results
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()