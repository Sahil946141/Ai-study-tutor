import streamlit as st

from api_client import explain_topic


def run():
    st.title("Ask AI Tutor")
    st.write("Enter a topic and grade level, then click Explain to get a simple AI-powered explanation.")

    topic = st.text_input("Topic", value="", key="ask_topic")
    grade_level = st.selectbox(
        "Grade level",
        ["Elementary", "Middle school", "High school", "College"],
        key="ask_grade_level",
    )

    if st.button("Explain", key="ask_explain"):
        if not topic.strip():
            st.warning("Please enter a topic to explain.")
            return

        with st.spinner("Generating explanation..."):
            response = explain_topic(topic, grade_level)

        if "error" in response:
            st.error(f"Error: {response['error']}")
            return

        st.subheader("Explanation")
        st.write(response.get("explanation", "-"))

        st.subheader("Example")
        st.write(response.get("example", "-"))

        st.subheader("Key Points")
        key_points = response.get("key_points") or []
        for point in key_points:
            st.write(f"- {point}")
