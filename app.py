import streamlit as st
import openai
import os

# Load API key from Streamlit Secrets
openai.api_key = os.environ["OPENAI_API_KEY"]

# Page config
st.set_page_config(page_title="AI Tutor")

# UI
st.title("🧠 AI Reasoning Tutor")
st.write("Ask any math question and get step-by-step solution.")

# Input
question = st.text_input("Enter a math question:")

# Button
if st.button("Solve"):
    if question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful math tutor. Solve step-by-step clearly."},
                        {"role": "user", "content": question}
                    ]
                )

                answer = response["choices"][0]["message"]["content"]

                st.success("Solution:")
                st.write(answer)

            except Exception as e:
                st.error("Something went wrong. Please check your API key or try again.")
                st.text(str(e))
