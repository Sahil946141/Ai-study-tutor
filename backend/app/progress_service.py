from app.db import get_connection


def get_user_progress(user_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT total_points, level
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )
        user_row = cursor.fetchone()

        if not user_row:
            return {
                "user_id": user_id,
                "total_points": 0,
                "level": 1,
                "quizzes_attempted": 0,
                "average_score": 0,
                "badges": [],
                "topic_performance": {}
            }

        total_points = user_row[0]
        level = user_row[1]

        cursor.execute(
            """
            SELECT COUNT(*), COALESCE(AVG((score::float / NULLIF(total, 0)) * 100), 0)
            FROM quiz_attempts
            WHERE user_id = %s
            """,
            (user_id,)
        )
        attempts_row = cursor.fetchone()
        quizzes_attempted = attempts_row[0]
        average_score = round(float(attempts_row[1]), 2)

        cursor.execute(
            """
            SELECT badge_name
            FROM badges
            WHERE user_id = %s
            ORDER BY awarded_at ASC
            """,
            (user_id,)
        )
        badge_rows = cursor.fetchall()
        badges = [row[0] for row in badge_rows]

        cursor.execute(
    """
    SELECT INITCAP(LOWER(q.topic)) AS topic,
           ROUND(AVG((qa.score::float / NULLIF(qa.total, 0)) * 100)::numeric, 2) AS avg_topic_score
    FROM quiz_attempts qa
    JOIN quizzes q ON qa.quiz_id = q.id
    WHERE qa.user_id = %s
    GROUP BY INITCAP(LOWER(q.topic))
    ORDER BY topic
    """,
    (user_id,)
)
        topic_rows = cursor.fetchall()

        topic_performance = {
            row[0]: float(row[1]) for row in topic_rows
        }

        return {
            "user_id": user_id,
            "total_points": total_points,
            "level": level,
            "quizzes_attempted": quizzes_attempted,
            "average_score": average_score,
            "badges": badges,
            "topic_performance": topic_performance
        }

    finally:
        cursor.close()
        conn.close()