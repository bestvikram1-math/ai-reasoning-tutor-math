import streamlit as st
from openai import OpenAI
import os

# Load API key
client = OpenAI()

st.set_page_config(page_title="AI Tutor")

st.title("🧠 AI Reasoning Tutor")
st.write("Ask any math question and get step-by-step solution.")

question = st.text_input("Enter a math question:")

if st.button("Solve"):
    if question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful math tutor."},
                    {"role": "user", "content": question}
                ]
            )

            answer = response.choices[0].message.content

            st.success("Solution:")
            st.write(answer)
