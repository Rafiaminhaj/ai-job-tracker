import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger(__name__)

TARGET_HR_LIST = [
    {
        "company": "Enginow (Hiring Hackathon S1)",
        "hr_email": "build.wt@enginow.in",
        "job_title": "AI / Software Engineer Intern (Hackathon Candidate)"
    },
    {
        "company": "Swiggy",
        "hr_email": "careers@swiggy.in",
        "job_title": "Software Engineer Intern (Backend)"
    },
    {
        "company": "Flipkart",
        "hr_email": "careers@flipkart.com",
        "job_title": "SDE Intern"
    },
    {
        "company": "Amazon India",
        "hr_email": "careers@amazon.in",
        "job_title": "Software Development Engineer Intern"
    },
    {
        "company": "IBM India",
        "hr_email": "careers.in@ibm.com",
        "job_title": "Software Developer Intern"
    },
    {
        "company": "Juspay",
        "hr_email": "careers@juspay.in",
        "job_title": "Backend Engineer Intern"
    }
]

def dispatch_all_real_hr_emails():
    """
    Connects to Gmail SMTP using Rafia's App Password and dispatches actual,
    real cold outreach emails directly from rafiaminhaj423@gmail.com to HR recruiter emails!
    """
    sender_email = settings.SENDER_EMAIL or "rafiaminhaj423@gmail.com"
    sender_password = settings.SENDER_APP_PASSWORD or "tbgnjvpccnipopoq"

    if not sender_password:
        print("Error: SENDER_APP_PASSWORD not set in .env")
        return False

    print(f"Connecting to Gmail SMTP server using {sender_email}...")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)

    results = []
    for item in TARGET_HR_LIST:
        company = item["company"]
        target_hr = item["hr_email"]
        job_title = item["job_title"]

        msg = MIMEMultipart()
        msg['From'] = f"Rafia Minhaj <{sender_email}>"
        msg['To'] = target_hr
        msg['Subject'] = f"Application for {job_title} - Rafia Minhaj (B.Tech CSE '27, CIT Ranchi)"

        body = f"""Dear Hiring Team at {company},

I hope this email finds you well.

My name is Rafia Minhaj, a B.Tech Computer Science & Engineering student (Class of 2027) at Cambridge Institute of Technology (CIT), Ranchi. I am writing to express my strong interest in the {job_title} role at {company}.

Key Highlights of My Candidate Profile:
- Global Open-Source Contributor (GirlScript Summer of Code GSSoC '26 Rank #29 globally)
- Google Cloud Code Kitchen Reality Audition Score: 95/100
- Technical Skills: Python, FastAPI, Gemini AI Agent Workflows, Docker, Webhooks, SQL, HTML/CSS
- Online Portfolio: https://rafiaminhaj.github.io/my-portfolio/
- Verified Resume PDF: https://rafiaminhaj.github.io/my-portfolio/Rafia_Minhaj_Resume.pdf

I have attached my verified resume link and would welcome the opportunity to discuss how my technical skills and problem-solving abilities align with your engineering team's goals.

Thank you for your time and consideration.

Best regards,

Rafia Minhaj
Phone: +91-6206675008
Email: {sender_email}
GitHub: https://github.com/Rafiaminhaj
Portfolio: https://rafiaminhaj.github.io/my-portfolio/
"""
        msg.attach(MIMEText(body, 'plain'))

        try:
            server.send_message(msg)
            print(f"SUCCESS: Real HR Email Sent to {company} ({target_hr})!")
            results.append({"company": company, "hr_email": target_hr, "status": "SENT"})
        except Exception as e:
            print(f"FAILED to send to {company} ({target_hr}): {e}")
            results.append({"company": company, "hr_email": target_hr, "status": "FAILED", "error": str(e)})

    server.quit()
    print("All HR emails processed!")
    return results

if __name__ == "__main__":
    dispatch_all_real_hr_emails()
