# 📬 ResumeMailer AI

ResumeMailer AI is a one-click intelligent assistant designed to automate your job application workflow. It reads your resume, analyzes job descriptions, matches key skills, personalizes email templates, and sends tailored job application emails to HR contacts — all while keeping track of where you applied and when.

Whether you're applying for 5 or 50 jobs, ResumeMailer AI makes the process seamless, fast, and organized.

---

## 🚀 Key Features

### ✅ Smart Resume Matching
- Extracts skills and experience from your resume
- Compares them with the job description
- Calculates a **matching score** to help prioritize applications

### ✅ Multi-Template Email System
- Choose from **pre-written professional templates**
- Personalize with auto-filled fields (name, company, role, etc.)
- Easily editable before sending

### ✅ Job Application Tracker (CSV)
- Each time you send a mail, the tool logs:
  - Date
  - Company
  - Role
  - HR Email
  - Resume Match Score
- Automatically appends to a CSV file for future reference

### ✅ Keyword Highlighter
- Highlights matching keywords in both resume and job description
- Helps you tailor your applications more effectively

### ✅ Streamlit Dashboard
- Intuitive UI to enter job details and trigger application emails
- See matching score, preview emails, and track applications visually

### ✅ One-Click Email Sending
- Connects to your email using SMTP
- Sends customized emails with your resume attached
- No manual Gmail/Outlook composing needed

### ✅ Voice & AI-Powered Modules (Planned)
- 🔄 Resume & Cover Letter Generator (Temporarily Disabled)
- 🎤 Voice to PPT Creator for Interview Prep (Coming Soon)

---

## 💡 How It Works

1. Upload your resume (PDF format)
2. Enter the job title, company name, and HR email
3. Paste the job description
4. Choose your preferred email template
5. Click **Send Mail**
6. Your job application is sent and logged in the CSV tracker

---

## 🖥️ Demo & Screenshots

### 🎥 Demo Video  
Watch ResumeMailer AI in action: [🔗 YouTube Video Link]

### 🖼️ Screenshots  
| Dashboard | Job Tracker |
|----------|--------------|
| ![Dashboard](screenshots/dashboard.png) | ![Tracker](screenshots/tracker.png) |

---

## 🛠️ Tech Stack

| Layer         | Technology                     |
|---------------|-------------------------------|
| Frontend UI   | Streamlit                     |
| Backend       | Python                        |
| PDF Handling  | `fpdf` (Resume/Cover Letter)  |
| Email Sending | `smtplib`, `email.message`    |
| File I/O      | `pandas`, `csv`               |
| NLP Matching  | Basic string & keyword match  |
| Add-ons       | OpenAI (optional), Speech-to-PPT module (upcoming)

---

## 🔧 Installation & Setup

1. **Clone the repository**

git clone https://github.com/yourusername/ResumeMailerAI.git
cd ResumeMailerAI 

2. ** Run the app**

streamlit run app.py


---

## 📁 Output Files
All sent job applications are logged in job_tracker.csv

Optionally generated PDFs (Resume / Cover Letter) are stored in /PDF folder

---

## 🔐 Security Notes
Your email credentials are never stored

The app uses local SMTP for sending emails

To be extra safe, use an App Password instead of your real password

---

## 📌 Upcoming Features
🧠 Resume & Cover Letter Generator via GPT (currently paused)

🎤 Voice-to-PPT module for automatic presentation building

🔍 Smart LinkedIn/Naukri scraper for new job listings

📅 Calendar integration for follow-up reminders

---

## 🙋‍♂️ Why I Built This
Job hunting can be exhausting, especially when applying to multiple companies daily. I wanted to build something that not only automates the repetitive parts (emailing, tracking, customizing) but also adds a layer of intelligence through keyword matching and personalization.

Whether you're applying to your dream job or mass applying during layoffs, ResumeMailer AI saves you hours every week.

## 🙌 Contribute or Connect
If you'd like to contribute to this project, open a PR or reach out!

📫 Email: darshshah.cs@gmail.com
🔗 LinkedIn: https://www.linkedin.com/in/your-profile

⭐ Show Your Support
If this project helped you in any way, consider giving it a ⭐ on GitHub and sharing it with your network!
