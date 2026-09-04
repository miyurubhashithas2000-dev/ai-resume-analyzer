import time
import os
import json
import pdfplumber
import streamlit as st
from dotenv import load_dotenv
from google import genai
from database import init_db, save_analysis, get_all_history
from pdf_generator import generate_pdf_report

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Initialize database
init_db()


def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def analyze_resume(resume_text, job_description):
    prompt = f"""
You are an expert career coach and resume reviewer.

Analyze the following RESUME against the given JOB DESCRIPTION.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Respond ONLY with valid JSON in exactly this format (no extra text, no markdown code blocks):

{{
  "match_score": <a number between 0 and 100>,
  "missing_keywords": ["keyword1", "keyword2", "..."],
  "strengths": ["strength1", "strength2", "..."],
  "weaknesses": ["weakness1", "weakness2", "..."],
  "suggestions": ["suggestion1", "suggestion2", "..."]
}}
"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            return json.loads(raw_text)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(5)  # wait 5 seconds before retrying
                continue
            else:
                raise e


# ---------------- STREAMLIT UI ----------------

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="centered")

with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    This AI-powered tool analyzes your resume against a job description 
    and gives you actionable feedback to improve your chances of landing 
    an interview.
    """)
    st.write("**How to use:**")
    st.write("1. Upload your resume (PDF)")
    st.write("2. Paste the job description")
    st.write("3. Click 'Analyze Resume'")
    st.write("4. Review feedback & download report")
    
    st.divider()
    st.caption("Built with Python, Streamlit & Gemini AI")

st.title("📄 AI-Powered Resume Analyzer")
st.write("Upload your resume and paste a job description to get instant AI feedback.")
st.divider()

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
with col2:
    st.write("**Tips for best results:**")
    st.caption("• Use a text-based PDF (not scanned image)")
    st.caption("• Paste the full job description")
    st.caption("• Include specific requirements & skills")

job_description = st.text_area("Paste the Job Description here", height=200)

if st.button("Analyze Resume", type="primary"):
    if uploaded_file is not None and job_description.strip() != "":
        with st.spinner("Analyzing your resume... please wait"):
            resume_text = extract_text_from_pdf(uploaded_file)
            try:
                result = analyze_resume(resume_text, job_description)
                save_analysis(job_description, result)
                pdf_bytes = generate_pdf_report(result, job_description)

                st.success("Analysis Complete!")

                # Match Score
                st.subheader("🎯 Match Score")
                score = result["match_score"]
                st.progress(score / 100)
                st.write(f"**{score}%** match with this job")

                # Missing Keywords
                st.subheader("🔑 Missing Keywords")
                if result["missing_keywords"]:
                    st.write(", ".join(result["missing_keywords"]))
                else:
                    st.write("None — great coverage!")

                # Strengths
                st.subheader("💪 Strengths")
                for item in result["strengths"]:
                    st.markdown(f"- {item}")

                # Weaknesses
                st.subheader("⚠️ Weaknesses")
                for item in result["weaknesses"]:
                    st.markdown(f"- {item}")

                # Suggestions
                st.subheader("💡 Suggestions")
                for item in result["suggestions"]:
                    st.markdown(f"- {item}")

                # Download button
                st.divider()
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name="resume_analysis_report.pdf",
                    mime="application/pdf"
                )

            except json.JSONDecodeError:
                st.error("The AI response couldn't be processed. Please try again.")
    else:
        st.error("Please upload a resume AND paste a job description before analyzing.")


# ---------------- HISTORY SECTION ----------------

st.divider()
st.subheader("📜 Past Analyses")

history = get_all_history()

if history:
    for row in history:
        with st.expander(f"🗓️ {row[1]} — Score: {row[3]}%"):
            st.write(f"**Job Description:** {row[2][:200]}...")
            st.write(f"**Missing Keywords:** {row[4]}")
            st.write(f"**Strengths:** {row[5]}")
            st.write(f"**Weaknesses:** {row[6]}")
            st.write(f"**Suggestions:** {row[7]}")
else:
    st.write("No past analyses yet.")