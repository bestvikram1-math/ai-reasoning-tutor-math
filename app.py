import streamlit as st
import openai
import os

# Load API key
openai.api_key = os.environ["OPENAI_API_KEY"]

st.set_page_config(page_title="AI Tutor")

st.title("🧠 AI Reasoning Tutor")
st.write("Solve math questions with step-by-step solutions in LaTeX.")

# Mode selection
mode = st.selectbox("Choose Mode:", ["Quick Solve", "Guided Mode"])

# Input
question = st.text_input("Enter a math question:")

# -------------------------
# QUICK SOLVE MODE
# -------------------------
if mode == "Quick Solve":

    if st.button("Solve"):
        if question.strip() == "":
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):

                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": """You are a math tutor.

IMPORTANT RULES:
- Use LaTeX for ALL math expressions.
- Use $$...$$ for equations.
- Show step-by-step solution.
- Clearly highlight final answer.
"""
                            },
                            {"role": "user", "content": question}
                        ]
                    )

                    answer = response["choices"][0]["message"]["content"]

                    # Fallback: enforce LaTeX
                    if "$$" not in answer:
                        fix = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "Convert all math expressions into LaTeX using $$...$$."},
                                {"role": "user", "content": answer}
                            ]
                        )
                        answer = fix["choices"][0]["message"]["content"]

                    st.success("✅ Solution:")
                    st.markdown(answer)

                except Exception as e:
                    st.error("Error occurred")
                    st.text(str(e))


# -------------------------
# GUIDED MODE
# -------------------------
elif mode == "Guided Mode":

    st.write("🤝 Let's solve step-by-step together.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Start guided session
    if st.button("Start Guided Solving"):
        if question.strip() == "":
            st.warning("Enter a question first.")
        else:
            st.session_state.chat_history = [
                {
                    "role": "system",
                    "content": """You are a math tutor.

DO NOT give full solution.
Ask one step at a time.
Guide the student interactively.
Use LaTeX for math."""
                },
                {"role": "user", "content": question}
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.chat_history
            )

            reply = response["choices"][0]["message"]["content"]

            st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # Show chat
    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            st.markdown(f"🤖 {msg['content']}")
        elif msg["role"] == "user":
            st.markdown(f"👤 {msg['content']}")

    # User step input
    user_input = st.text_input("Your step / answer:")

    if st.button("Submit Step"):
        if user_input.strip() != "":
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.chat_history
            )

            reply = response["choices"][0]["message"]["content"]

            st.session_state.chat_history.append({"role": "assistant", "content": reply)
