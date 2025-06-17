import streamlit as st
import os
import json
import tempfile
import re
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from PyPDF2 import PdfReader
import requests
import base64
import urllib.parse
import webbrowser
from fpdf import FPDF
import pandas as pd
import datetime
from difflib import SequenceMatcher
from collections import Counter
import string

# --- Config ---
TRACKER_CSV = "Databases/job_applications_tracker.csv"

# Streamlit UI Setup
st.set_page_config(page_title="ResumeMailer AI", layout="centered")
st.title("📧 AI-Powered Resume Emailer")
st.progress(25, text="Step 1 of 5: Upload Resume")

# Step 1: Upload Resume
resume_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

st.markdown("---")
st.progress(50, text="Step 2 of 5: Email Details")

# Step 2: Enter Email Details
to_email = st.text_input("To Email Address", placeholder="recipient@company.com")

def extract_hr_and_company(email):
    match = re.match(r"([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+)\\.com", email)
    if match:
        user, domain = match.groups()
        hr_name = user.replace('.', ' ').split()[0].capitalize()
        company = domain.split(".")[0].capitalize()
        return hr_name, company
    return "", ""

hr_name, detected_company = extract_hr_and_company(to_email)
company_name = st.text_input("Company Name", value=detected_company)

st.markdown("---")
st.progress(75, text="Step 3 of 5: Job Info & Preferences")

job_description = st.text_area("Paste the job description (optional)", height=150)

def detect_job_role(text):
    lines = text.split("\n")
    for line in lines:
        if "Role:" in line or "Position:" in line:
            return line.split(":")[-1].strip()
    return ""

detected_role = detect_job_role(job_description) if job_description else ""
job_role = st.text_input("Job Role", value=detected_role or "")

email_subject = st.text_input("Email Subject (auto-suggested)", value=f"Application for {job_role or 'Job Role'}")

# Email Tone Options
email_tone = st.selectbox("Choose Email Tone", ["Professional", "Enthusiastic", "Direct"])

# Smart Matching Score
def get_groq_match_score(resume_text, job_desc, api_key):
    prompt = f"""
Compare the following resume and job description and output a match score from 0 to 100 based on relevance.

Resume:
{resume_text[:4000]}

Job Description:
{job_desc or "General position"}

Respond in the format: Match Score: <number>
"""
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.5,
            },
            timeout=30,
        )
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            match = re.search(r"Match Score: *(\d+)", content)
            if match:
                return int(match.group(1))
        return 0
    except Exception:
        return 0


# Checkboxes
add_cover_letter = st.checkbox("📝 Generate a tailored Cover Letter PDF")
generate_questions = st.checkbox("🎯 Generate Interview Questions")
submit_draft = st.button("🌐 Open Gmail Draft in Browser")

# Use hardcoded Groq API Key
groq_api_key = "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"

@st.cache_data
def extract_pdf_text(pdf_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_file.getvalue())
            reader = PdfReader(tmp.name)
            text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        os.unlink(tmp.name)
        return text
    except Exception as e:
        st.error(f"❌ Error extracting PDF text: {e}")
        return ""

def generate_email_from_resume(resume_text, job_desc, subject, hr_name, company, api_key, tone):
    tone_instructions = {
        "Professional": "Maintain a formal and respectful tone.",
        "Enthusiastic": "Express genuine enthusiasm and passion.",
        "Direct": "Be clear, concise, and confident."
    }
    prompt = f"""
You are a career assistant. Draft a job application email.
Tone: {tone_instructions.get(tone, 'Professional')}
RESUME:\n{resume_text[:4000]}
JOB DESCRIPTION:\n{job_desc or "General position application"}
EMAIL SUBJECT:\n{subject}
To: {'Dear ' + hr_name if hr_name else 'Dear HR'}
Company: {company or 'the company'}
Instructions:
- Professional greeting and closing
- Mention skills from resume
- Attach resume
"""
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.7,
            },
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return "Failed to generate email."
    except Exception as e:
        return f"Error generating email: {e}"

def generate_interview_questions(resume_text, job_desc, api_key):
    prompt = f"""
Generate 10-20 likely interview questions with high-quality sample answers based on the resume and the job description.
RESUME:\n{resume_text[:4000]}
JOB DESCRIPTION:\n{job_desc or "General position"}
Format:
Q: <question>\nA: <answer>
"""
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1500,
                "temperature": 0.7,
            },
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return "Failed to generate interview questions."
    except Exception as e:
        return f"Error generating questions: {e}"

def generate_cover_letter(resume_text, job_desc, company, hr_name, api_key):
    prompt = f"""
Write a professional cover letter.
RESUME:\n{resume_text[:4000]}
JOB DESCRIPTION:\n{job_desc or "General position"}
To: {'Dear ' + hr_name if hr_name else 'Dear HR'}
Company: {company}
"""
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.7,
            },
            timeout=30,
        )
        if response.status_code == 200:
            cover_letter = response.json()["choices"][0]["message"]["content"]
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in cover_letter.split('\n'):
                pdf.multi_cell(190, 10, line)
            safe_company = re.sub(r'[\\/*?:"<>|]', "_", company) or "company"
            filename = f"CoverLetter_{safe_company}.pdf"
            save_dir = r"C:\Users\10102\OneDrive\Desktop\Gen AI Project\RESUME MAILER\PDF"
            os.makedirs(save_dir, exist_ok=True)
            pdf_path = os.path.join(save_dir, filename)
            pdf.output(pdf_path)
            return pdf_path
        else:
            return None
    except Exception:
        return None


def save_questions_to_pdf(questions, company):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in questions.split('\n'):
        pdf.multi_cell(0, 10, line)
    safe_company = re.sub(r'[\\/*?:"<>|]', "_", company) or "company"
    filename = f"InterviewQs_{safe_company}.pdf"
    save_dir = r"C:\Users\10102\OneDrive\Desktop\Gen AI Project\RESUME MAILER\PDF"
    os.makedirs(save_dir, exist_ok=True)
    pdf_path = os.path.join(save_dir, filename)
    pdf.output(pdf_path)
    return pdf_path


def open_gmail_draft(recipient, subject, body):
    mailto_link = (
        f"https://mail.google.com/mail/?view=cm&fs=1&to={recipient}"
        f"&su={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    )
    webbrowser.open(mailto_link)
    st.success("✅ Draft opened in Gmail. Please review and send.")

# def highlight_keywords(body, keywords):
#     for word in sorted(keywords, key=len, reverse=True):
#         body = re.sub(rf"\\b{re.escape(word)}\\b", f"**{word}**", body, flags=re.IGNORECASE)
#     return body

def log_application(hr_email, company, role, score):
    os.makedirs(os.path.dirname(TRACKER_CSV), exist_ok=True)
    df = pd.DataFrame([[datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), hr_email, company, role, score]],
                      columns=["Date", "HR Email", "Company", "Job Role", "Match Score"])
    if os.path.exists(TRACKER_CSV):
        existing = pd.read_csv(TRACKER_CSV)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv(TRACKER_CSV, index=False)

if submit_draft:
    if not resume_file or not groq_api_key or not to_email:
        st.error("❌ Please provide resume and recipient email.")
    else:
        resume_text = extract_pdf_text(resume_file)
        if not resume_text:
            st.error("❌ Resume text extraction failed.")
        else:
            match_score = get_groq_match_score(resume_text, job_description, groq_api_key)
            st.markdown(f"#### ✅ AI Resume Match Score (via Groq): {match_score}%")


            email_body = generate_email_from_resume(resume_text, job_description, email_subject, hr_name, company_name, groq_api_key, email_tone)
            highlighted_body = email_body


            st.subheader("📄 Email Preview")
            final_body = st.text_area("Edit email before opening draft:", highlighted_body, height=300)
            open_gmail_draft(to_email, email_subject, final_body)

            log_application(to_email, company_name, job_role, match_score)

            if generate_questions:
                st.subheader("📘 Interview Questions")
                questions = generate_interview_questions(resume_text, job_description, groq_api_key)
                st.text_area("Review or copy these:", questions, height=300)
                pdf_path = save_questions_to_pdf(questions, company_name)
                with open(pdf_path, "rb") as f:
                    st.download_button("📥 Download Interview Questions PDF", f, file_name="interview_questions.pdf")

            if add_cover_letter:
                cover_path = generate_cover_letter(resume_text, job_description, company_name, hr_name, groq_api_key)
                if cover_path:
                    with open(cover_path, "rb") as f:
                        st.download_button("📄 Download Cover Letter PDF", f, file_name="cover_letter.pdf")

st.markdown("---")
st.subheader("📊 Application Tracker")
if os.path.exists(TRACKER_CSV):
    df = pd.read_csv(TRACKER_CSV)
    st.dataframe(df)

st.caption("✨ Built with 💼 AI resume intelligence | ResumeMailer AI")
