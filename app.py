import streamlit as st
from openai import OpenAI
import os
import base64

# Initialize client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

st.set_page_config(page_title="AI Tutor")

st.title("🧠 AI Reasoning Tutor (GPT-4o)")
st.write("Solve math problems with step-by-step LaTeX solutions.")

# Mode selection
mode = st.selectbox("Choose Mode:", ["Quick Solve", "Guided Mode"])

# Text input
question = st.text_input("Enter a math question:")

# Image upload
uploaded_file = st.file_uploader("Or upload an image", type=["png", "jpg", "jpeg"])

image_base64 = None

if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    st.image(uploaded_file, caption="Uploaded Image")

# -------------------------
# QUICK SOLVE MODE
# -------------------------
if mode == "Quick Solve":

    if st.button("Solve"):
        if not question and not image_base64:
            st.warning("Please enter a question or upload an image.")
        else:
            with st.spinner("Thinking..."):

                try:
                    # Build message
                    user_content = []

                    if question:
                        user_content.append({"type": "text", "text": question})

                    if image_base64:
                        user_content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        })

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": """
You are an expert math tutor.

STRICT RULES:
- Use LaTeX for ALL math expressions.
- Use $$...$$ for equations.
- Provide step-by-step solution.
- Highlight final answer clearly.
"""
                            },
                            {
                                "role": "user",
                                "content": user_content
                            }
                        ]
                    )

                    answer = response.choices[0].message.content

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

    if st.button("Start Guided Solving"):
        if not question:
            st.warning("Enter a question first.")
        else:
            st.session_state.chat_history = [
                {
                    "role": "system",
                    "content": """
You are a math tutor.

DO NOT give full solution.
Ask one step at a time.
Guide the student interactively.
Use LaTeX for math expressions.
"""
                },
                {"role": "user", "content": question}
            ]

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.chat_history
            )

            reply = response.choices[0].message.content

            st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # Show conversation
    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            st.markdown(f"🤖 {msg['content']}")
        elif msg["role"] == "user":
            st.markdown(f"👤 {msg['content']}")

    user_input = st.text_input("Your step / answer:")

    if st.button("Submit Step"):
        if user_input.strip() != "":
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.chat_history
            )

            reply = response.choices[0].message.content

            st.session_state.chat_history.append({"role": "assistant", "content": reply})
