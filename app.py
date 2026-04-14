import streamlit as st
from openai import OpenAI
import os
import base64
import time

# -------------------------
# INIT
# -------------------------
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

st.set_page_config(page_title="AI Tutor")

st.title("🧠 AI Reasoning Tutor (GPT-4o)")
st.write("Solve math problems step-by-step with AI.")

# -------------------------
# USAGE LIMIT (10/day)
# -------------------------
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0
    st.session_state.reset_time = time.time()

# Reset after 24 hrs
if time.time() - st.session_state.reset_time > 86400:
    st.session_state.usage_count = 0
    st.session_state.reset_time = time.time()

st.write(f"📊 Usage today: {st.session_state.usage_count}/10")

# -------------------------
# MODE
# -------------------------
mode = st.selectbox("Choose Mode:", ["Quick Solve", "Guided Mode"])

# -------------------------
# INPUT
# -------------------------
question = st.text_input("Enter a math question:")

uploaded_file = st.file_uploader("Or upload an image", type=["png", "jpg", "jpeg"])

image_base64 = None

if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    st.image(uploaded_file, caption="Uploaded Image")

# -------------------------
# QUICK SOLVE
# -------------------------
if mode == "Quick Solve":

    if st.button("Solve"):

        if st.session_state.usage_count >= 10:
            st.warning("⚠️ Daily limit reached (10 queries).")
            st.stop()

        if not question and not image_base64:
            st.warning("Please enter a question or upload an image.")
        else:
            with st.spinner("Thinking..."):

                try:
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

RULES:
- Use LaTeX for all math expressions.
- Use $$...$$ for equations.
- Solve step-by-step.
- Clearly highlight final answer.
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

                    # increment usage
                    st.session_state.usage_count += 1

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

        if st.session_state.usage_count >= 10:
            st.warning("⚠️ Daily limit reached.")
            st.stop()

        if not question and not image_base64:
            st.warning("Enter a question or upload an image.")
        else:
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

        st.session_state.chat_history = [
            {
                "role": "system",
                "content": """
You are a math tutor.

DO NOT give full solution.
Ask one step at a time.
Guide the student interactively.
Use LaTeX for math.
"""
            },
            {
                "role": "user",
                "content": user_content
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.chat_history
        )

        reply = response.choices[0].message.content

        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )

        st.session_state.usage_count += 1

    # show conversation
    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            st.markdown(f"🤖 {msg['content']}")
        elif msg["role"] == "user":
            st.markdown(f"👤 {msg['content']}")

    user_input = st.text_input("Your step / answer:")

    if st.button("Submit Step"):

        if st.session_state.usage_count >= 10:
            st.warning("⚠️ Daily limit reached.")
            st.stop()

        if user_input.strip() != "":
            st.session_state.chat_history.append(
                {"role": "user", "content": user_input}
            )

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.chat_history
            )

            reply = response.choices[0].message.content

            st.session_state.chat_history.append(
                {"role": "assistant", "content": reply}
            )

            st.session_state.usage_count += 1
