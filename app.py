import streamlit as st

st.set_page_config(page_title="AI Tutor")

st.title("🧠 AI Reasoning Tutor")

st.write("✅ App is running successfully!")

question = st.text_input("Enter a math question:")

if st.button("Solve"):
    st.success(f"You entered: {question}")
