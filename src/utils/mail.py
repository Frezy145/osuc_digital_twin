# This module handles sending emails using SMTP

import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.utils.log import log_error, log_info

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL")

def email(subject, body, to=EMAIL_HOST_USER):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_HOST_USER
    msg["To"] = to

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls() if EMAIL_USE_TLS else server.startssl()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(msg)
            log_info("--MAIL-- Email sent successfully.")
    except Exception as e:
        log_error(f"--MAIL-- {e}")
