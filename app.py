import streamlit as st
import openai
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

st.set_page_config(page_title="AI Tutor")

st.title("🧠 AI Reasoning Tutor")
st.write("Learn by solving step-by-step.")

# Mode selection
mode = st.selectbox("Choose Mode:", ["Quick Solve", "Guided Mode"])

# Input
question = st.text_input("Enter a math question:")

# Session state for guided mode
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------
# QUICK SOLVE MODE
# -------------------------
if mode == "Quick Solve":

    if st.button("Solve"):
        if question.strip() == "":
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a math tutor. Solve step-by-step using LaTeX for all mathematical expressions. Use $$ for equations."},
                        {"role": "user", "content": question}
                    ]
                )

                answer = response["choices"][0]["message"]["content"]

                st.success("Solution:")
                st.markdown(answer, unsafe_allow_html=True)

# -------------------------
# GUIDED MODE
# -------------------------
elif mode == "Guided Mode":

    st.write("🤝 Let's solve this together step by step.")

    # Start conversation
    if st.button("Start Guided Solving"):
        if question.strip() == "":
            st.warning("Enter a question first.")
        else:
            st.session_state.chat_history = [
                {"role": "system", "content": "You are a math tutor. Do NOT give full solution. Ask step-by-step questions and guide the student."},
                {"role": "user", "content": question}
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.chat_history
            )

            reply = response["choices"][0]["message"]["content"]

            st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # Display chat
    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            st.write("🤖:", msg["content"])
        elif msg["role"] == "user":
            st.write("👤:", msg["content"])

    # User input for next step
    user_input = st.text_input("Your step / answer:")

    if st.button("Submit Step"):
        if user_input.strip() != "":
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.chat_history
            )

            reply = response["choices"][0]["message"]["content"]

            st.session_state.chat_history.append({"role": "assistant", "content": reply})
