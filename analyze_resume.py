import os
import pdfplumber
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
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

Provide your analysis in this exact structure:

1. MATCH SCORE: (a percentage from 0-100 representing how well the resume fits the job)

2. MISSING KEYWORDS: (list important skills/keywords from the job description that are missing in the resume)

3. STRENGTHS: (what the resume does well for this job)

4. WEAKNESSES: (what's missing or weak in the resume for this job)

5. SUGGESTIONS: (3-5 specific, actionable improvements)
"""
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text


# ---- Main Program ----

# Step 1: Extract resume text
resume_text = extract_text_from_pdf("sample_resume.pdf")

# Step 2: Paste a sample job description here
job_description = """
We are looking for a Software Engineer with experience in Python, 
REST APIs, SQL databases, and cloud platforms like AWS. 
The ideal candidate has strong problem-solving skills, experience with Git, 
and familiarity with Agile development practices.
"""

# Step 3: Get AI analysis
result = analyze_resume(resume_text, job_description)

# Step 4: Print result
print(result)