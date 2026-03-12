import streamlit as st

from api_client import generate_quiz, submit_quiz


def _get_answer_key(quiz_id: str, question_id: str) -> str:
    return f"quiz_{quiz_id}_q_{question_id}"


def _collect_answers(quiz_data: dict) -> dict:
    """Collect selected answers from session state for the current quiz."""
    answers = {}
    quiz_id = str(quiz_data.get("quiz_id"))
    for q in quiz_data.get("questions", []):
        question_id = str(q.get("question_id"))
        key = _get_answer_key(quiz_id, question_id)
        value = st.session_state.get(key)
        if value is not None:
            answers[question_id] = value
    return answers


def run():
    st.title("Practice Quiz")
    st.write("Generate a quiz, answer questions, and submit to see your score and rewards.")

    topic = st.text_input("Topic", value="", key="quiz_topic")
    difficulty = st.selectbox(
        "Difficulty", ["Easy", "Medium", "Hard"], key="quiz_difficulty"
    )
    num_questions = st.slider(
        "Number of questions", min_value=1, max_value=10, value=3, key="quiz_num_questions"
    )

    if st.button("Generate Quiz"):
        if not topic.strip():
            st.warning("Please enter a topic to generate a quiz.")
        else:
            with st.spinner("Generating quiz..."):
                response = generate_quiz(topic, difficulty, num_questions)

            if "error" in response:
                st.error(f"Error: {response['error']}")
            else:
                st.session_state.current_quiz = response
                st.session_state.quiz_result = None
                st.success("Quiz generated! Scroll down to answer the questions.")

    current_quiz = st.session_state.get("current_quiz")

    if not current_quiz:
        st.info("Generate a quiz to start practicing.")
        return

    st.subheader(f"Quiz: {current_quiz.get('topic')} ({current_quiz.get('difficulty')})")

    # Render questions
    for idx, question in enumerate(current_quiz.get("questions", []), start=1):
        question_id = str(question.get("question_id"))
        st.write(f"**Question {idx}:** {question.get('question')}" )
        key = _get_answer_key(str(current_quiz.get("quiz_id")), question_id)
        st.radio(
            "Select an answer:",
            question.get("options", []),
            key=key,
            label_visibility="collapsed",
        )

    if st.button("Submit Quiz"):
        answers = _collect_answers(current_quiz)
        if len(answers) != len(current_quiz.get("questions", [])):
            st.warning("Please answer all questions before submitting.")
        else:
            with st.spinner("Submitting your answers..."):
                result = submit_quiz(
                    user_id=st.session_state.user_id,
                    quiz_id=str(current_quiz.get("quiz_id")),
                    answers=answers,
                )

            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.session_state.quiz_result = result
                st.success("Quiz submitted! See your results below.")

    quiz_result = st.session_state.get("quiz_result")

    if quiz_result:
        st.markdown("---")
        st.subheader("Results")

        score = quiz_result.get("score")
        total = quiz_result.get("total")
        points = quiz_result.get("points_earned")
        new_points = quiz_result.get("new_total_points")
        new_level = quiz_result.get("new_level")

        st.success(f"Score: {score} / {total}")
        st.info(f"Points earned: {points} | Total points: {new_points} | Level: {new_level}")

        badges = quiz_result.get("badges_awarded") or []
        if badges:
            st.subheader("Badges earned")
            for badge in badges:
                st.write(f"- {badge}")

        st.subheader("Question review")
        for result in quiz_result.get("results", []):
            correctness = result.get("is_correct")
            label = "Correct" if correctness else "Incorrect"
            emoji = "✅" if correctness else "❌"
            st.markdown(f"**{emoji} {label}:** {result.get('question')}  ")
            st.write(f"- Your answer: {result.get('your_answer')}  ")
            st.write(f"- Correct answer: {result.get('correct_answer')}  ")
            st.info(f"Explanation: {result.get('explanation')}" )
