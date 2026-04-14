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

st.title("🧠 AI Reasoning Tutor (Smart Mode)")
st.write("Now with verification + confidence + step validation.")

# -------------------------
# USAGE LIMIT
# -------------------------
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0
    st.session_state.reset_time = time.time()

if time.time() - st.session_state.reset_time > 86400:
    st.session_state.usage_count = 0
    st.session_state.reset_time = time.time()

st.write(f"📊 Usage today: {st.session_state.usage_count}/10")

# -------------------------
# MODEL SELECTOR
# -------------------------
def choose_model(question, has_image):
    if has_image:
        return "gpt-4o"
    if question and len(question) < 80:
        return "gpt-3.5-turbo"
    return "gpt-4o"

# -------------------------
# INPUT
# -------------------------
question = st.text_input("Enter a math question:")

uploaded_file = st.file_uploader("Upload image (optional)", type=["png", "jpg", "jpeg"])

image_base64 = None
if uploaded_file:
    image_bytes = uploaded_file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    st.image(uploaded_file, caption="Uploaded Image")

# -------------------------
# SOLVE FUNCTION
# -------------------------
def solve_and_verify(question, image_base64, model):

    user_content = []

    if question:
        user_content.append({"type": "text", "text": question})

    if image_base64:
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{image_base64}"}
        })

    # STEP 1: SOLVE
    solve_response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": """
You are an expert mathematician.

- Solve rigorously.
- Use LaTeX for all math.
- Show step-by-step solution.
"""
            },
            {"role": "user", "content": user_content}
        ]
    )

    solution = solve_response.choices[0].message.content

    # STEP 2: VERIFY
    verify_response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": """
Check if the solution is mathematically correct.
If incorrect, fix it completely.
Return final corrected solution.
"""
            },
            {"role": "user", "content": solution}
        ]
    )

    verified_solution = verify_response.choices[0].message.content

    # STEP 3: CONFIDENCE SCORE
    confidence_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Give confidence score (0-100) for correctness and explain briefly."
            },
            {"role": "user", "content": verified_solution}
        ]
    )

    confidence = confidence_response.choices[0].message.content

    return verified_solution, confidence

# -------------------------
# STEP VALIDATION
# -------------------------
def validate_step(question, step):

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": """
Check if the student's step is correct.
- If correct → say why
- If wrong → explain mistake and guide next step
"""
            },
            {
                "role": "user",
                "content": f"Question: {question}\nStudent Step: {step}"
            }
        ]
    )

    return response.choices[0].message.content

# -------------------------
# BUTTON: SOLVE
# -------------------------
if st.button("Solve"):

    if st.session_state.usage_count >= 10:
        st.warning("⚠️ Daily limit reached.")
        st.stop()

    if not question and not image_base64:
        st.warning("Enter a question or upload an image.")
    else:
        with st.spinner("Thinking..."):

            model = choose_model(question, image_base64 is not None)

            solution, confidence = solve_and_verify(question, image_base64, model)

            st.success("✅ Verified Solution:")
            st.markdown(solution)

            st.info("📊 Confidence:")
            st.write(confidence)

            st.session_state.usage_count += 1

# -------------------------
# STEP VALIDATION UI
# -------------------------
st.subheader("🧠 Validate Your Step")

student_step = st.text_input("Enter your step:")

if st.button("Check Step"):

    if student_step.strip() == "":
        st.warning("Enter a step first.")
    else:
        feedback = validate_step(question, student_step)

        st.warning("📌 Feedback:")
        st.write(feedback)
