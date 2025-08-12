# app/services/send_html_email.py

import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS") 
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO").split(",") if os.getenv("EMAIL_TO") else []

class send_html_email:
    def __init__(self, html_fragment):
        if not EMAIL_TO:
            raise ValueError("No recipients set in EMAIL_TO")

        self.msg = MIMEMultipart("alternative")
        self.msg["From"] = EMAIL_FROM
        self.msg["To"] = ", ".join(EMAIL_TO)
        self.msg["Subject"] = "NCSL Legislative Digest"

        plain = "Please view this email in an HTML-capable client to see the legislative digest."
        part_plain = MIMEText(plain, "plain")
        part_html = MIMEText(html_fragment, "html")

        self.msg.attach(part_plain)
        self.msg.attach(part_html)

    def send(self):
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, self.msg.as_string())
