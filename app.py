import streamlit as st
import openai
import os
from PIL import Image
import pytesseract

# Load API key
openai.api_key = os.environ["OPENAI_API_KEY"]

st.set_page_config(page_title="AI Tutor")

st.title("🧠 AI Reasoning Tutor")
st.write("Solve math questions with proper formatting.")

# -------------------------
# INPUT: TEXT OR IMAGE
# -------------------------

question = st.text_input("Enter a math question:")

uploaded_file = st.file_uploader("Or upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    extracted_text = pytesseract.image_to_string(image)
    st.write("📄 Extracted text:", extracted_text)

    question = extracted_text  # override question

# -------------------------
# SOLVE BUTTON
# -------------------------

if st.button("Solve"):
    if question.strip() == "":
        st.warning("Please enter or upload a question.")
    else:
        with st.spinner("Thinking..."):

            try:
                # STEP 1: Solve with strict LaTeX instruction
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a math tutor.

IMPORTANT RULES:
- Use LaTeX for ALL math expressions.
- Use $$...$$ for equations.
- Do NOT use normal text like (x^2).
- Show step-by-step solution clearly.
- Highlight final answer separately.
"""
                        },
                        {"role": "user", "content": question}
                    ]
                )

                answer = response["choices"][0]["message"]["content"]

                # STEP 2: Ensure LaTeX formatting (fallback)
                if "$$" not in answer:
                    fix_response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "Convert all math expressions into LaTeX using $$...$$."
                            },
                            {"role": "user", "content": answer}
                        ]
                    )
                    answer = fix_response["choices"][0]["message"]["content"]

                # STEP 3: Display nicely
                st.success("✅ Solution:")
                st.markdown(answer)

            except Exception as e:
                st.error("Error occurred")
                st.text(str(e))
