import sys
from pathlib import Path

import streamlit as st

# Ensure "pages" package can be imported when running from different working directories.
APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from pages import ask_ai, progress, quiz


def main():
    st.set_page_config(
        page_title="AI Study Companion",
        layout="wide",
        initial_sidebar_state="auto",
    )

    st.title("AI Study Companion")
    st.markdown("A simple, demo-ready study tool powered by AI.")

    # Session state defaults
    if "current_quiz" not in st.session_state:
        st.session_state.current_quiz = None

    if "quiz_result" not in st.session_state:
        st.session_state.quiz_result = None

    # User ID input (fixed user for prototype, but editable)
    st.sidebar.markdown("### User")
    st.sidebar.text_input("User ID", value=st.session_state.get("user_id", "student1"), key="user_id")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Ask AI Tutor", "Practice Quiz", "Progress"],
        index=0,
    )

    if page == "Ask AI Tutor":
        ask_ai.run()
    elif page == "Practice Quiz":
        quiz.run()
    elif page == "Progress":
        progress.run()


if __name__ == "__main__":
    main()
