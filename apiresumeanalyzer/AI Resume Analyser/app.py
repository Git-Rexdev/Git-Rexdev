import os
import streamlit as st
# from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import pytesseract
import pdfplumber
import re

# Configure Google API Key
genai.configure(api_key="AIzaSyD-7uW0_vHEzYdLR9BTUUevHoDEmDgy6OM")

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

        if text.strip():
            return text.strip()

    except Exception as e:
        print(f"Direct text extraction failed: {e}")

    print("Falling back to OCR for image-based PDFs")
    try:
        text = pytesseract.image_to_string(pdf_path)
    except Exception as e:
        print(f"OCR extraction failed: {e}")

    return text.strip()

def analyze_resume(resume_text, job_description=None):
    if not resume_text:
        return {"error": "Resume text is required for analysis."}

    model = genai.GenerativeModel("gemini-2.0-flash")

    base_prompt = f"""
    You are an experienced HR with technical expertise. Analyze the provided resume based on skills, experience, and alignment with industry standards.
    Provide:
    - A professional evaluation of the candidate's profile.
    - Strengths and weaknesses.
    - Skills the candidate already has and suggested improvements.
    - Recommended courses to enhance skills. Suggest free links.
    - Suggest jobs based on resume.
    - If the resume has experience with some certain roles, predict future job roles.
    - Score the person's job readiness.
    - A score out of 100 based on relevance, skills, and overall quality.
    - Suggestions for resume improvements.

    Resume:
    {resume_text}
    """

    if job_description:
        base_prompt += f"""
        Additionally, compare the resume with the following job description and provide a detailed analysis:

        Job Description:
        {job_description}

        Highlight the strengths and weaknesses of the applicant in relation to the job description.
        """

    response = model.generate_content(base_prompt)
    analysis = response.text.strip()

    score = None
    match = re.search(r"(\b\d{1,3}\b)\s*/?\s*100", analysis)
    if match:
        score = match.group(1)

    return analysis, score

st.set_page_config(page_title="AI Resume Analyser", layout="wide")

st.title("AI Resume Analyser")
st.write("""
Upload your resume and compare it against a job description using our AI. 
Receive insights, suggestions, and a readiness score instantly.
""")

col1, col2 = st.columns([1, 1])
with col1:
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
with col2:
    job_description = st.text_area("Job Description", placeholder="Paste the job description here...")

if uploaded_file:
    st.success("Resume uploaded successfully!")
    with open("uploaded_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    resume_text = extract_text_from_pdf("uploaded_resume.pdf")
else:
    st.info(" Please upload your resume in PDF format.")

if st.button("Analyse Resume"):
    if uploaded_file:
        with st.spinner("\u23F3 Analyzing resume..."):
            try:
                analysis, score = analyze_resume(resume_text, job_description)

                if score:
                    st.markdown(f"## Resume Score: **{score}/100**")
                else:
                    st.warning("No score found in the response.")

                st.markdown("---")
                st.subheader("AI Insights:")
                st.markdown(f"<div style='white-space: pre-wrap;'>{analysis}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Analysis failed: {e}")
    else:
        st.warning("Upload your resume before analysis.")

st.markdown("""
---
<p style='text-align: center;'>Made by <b>Team Error-404</b> | Prabal 2025 GDG on Campus SGU</p>
""", unsafe_allow_html=True)