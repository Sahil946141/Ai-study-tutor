import streamlit as st
import pandas as pd

from api_client import get_progress


def run():
    st.title("Learning Progress")
    st.write("Track your points, level, badges, and topic performance.")

    user_id = st.session_state.get("user_id")
    with st.spinner("Loading progress..."):
        response = get_progress(user_id)

    if "error" in response:
        st.error(f"Error: {response['error']}")
        return

    total_points = response.get("total_points", 0)
    level = response.get("level", 1)
    quizzes_attempted = response.get("quizzes_attempted", 0)
    average_score = response.get("average_score", 0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total points", total_points)
    col2.metric("Level", level)
    col3.metric("Quizzes attempted", quizzes_attempted)
    col4.metric("Average score", f"{average_score}%")

    badges = response.get("badges") or []
    if badges:
        st.subheader("Badges")
        for badge in badges:
            st.write(f"- {badge}")

    topic_performance = response.get("topic_performance") or {}

    # Optionally hide certain topics from the progress view (e.g., placeholder/test topics)
    ignored_topics = {"photosynthesis"}
    filtered_topic_performance = {
        t: s
        for t, s in topic_performance.items()
        if t.lower() not in ignored_topics
    }

    if filtered_topic_performance:
        st.subheader("Topic performance")
        df = pd.DataFrame(
            list(filtered_topic_performance.items()), columns=["Topic", "Average Score"]
        )
        st.bar_chart(df.set_index("Topic"))

        st.subheader("Topics completed")
        for topic, score in filtered_topic_performance.items():
            st.write(f"- **{topic}** — Average score: {score}%")
    else:
        st.info("No topic performance data yet. Take a quiz to see your progress.")
