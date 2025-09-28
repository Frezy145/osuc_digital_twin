# This module handles sending emails using SMTP

from datetime import datetime,timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.utils.log import log_error, log_info
from src.utils.data import archive

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL")
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", EMAIL_HOST_USER).split(",")

def create_html_body(title, message, recipient_name=None, data_summary=None):
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                background-color: #f4f4f4;
                padding: 20px;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                margin-top: 20px;
                padding: 20px;
                background-color: white;
                border-radius: 0 0 5px 5px;
                font-size: 1.3em;
                color: #333;
            }}
            .data-summary {{
                margin-top: 20px;
                padding: 10px;
                background-color: #e8f5e9;
                border-radius: 5px;
            }}
            .data-summary h3 {{
                margin-top: 0;
            }}
            .data-summary ul {{
                list-style-type: none;
                padding: 0;
            }}
            .data-summary li {{
                margin-bottom: 5px;
            }}

            .footer {{
                margin-top: 20px;
                font-size: 1em;
                color: #777;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        
        <div class="header">
            <h2>{title}</h2>
        </div>

        <div class="content">
            <p><strong>Dear {recipient_name if recipient_name else "Valued Customer"},</strong></p>
            <p><strong>{message}</strong></p>
            {f'<div class="data-summary"><h3>Data Summary:</h3><ul>' + ''.join([f'<li>{key}: {value}</li>' for key, value in data_summary.items()]) + '</ul></div>' if data_summary else ''}
            <p><strong>Best regards,</strong></p>
            <p>
                <strong>OSUC Digital Twin System</strong><br>
                Observatoire des Sciences de l'Univers en Region Centre-Val de Loire (OSUC)<br>
                1A rue de la Ferollerie, 45071 Orléans Cedex 2, France<br>
                Universite d'Orleans.
                <br>
                <img src="https://geodata-osuc.eu/wp-content/uploads/2023/05/logo_osuc-1.jpg" alt="OSUC Logo" width="120"><br>
                <a href="https://www.univ-orleans.fr/fr/osuc" target="_blank">OSUC</a> | 
                <a href="https://www.univ-orleans.fr/" target="_blank">University d'Orleans</a> | 
                <a href="https://geodata-osuc.eu/luniversite-dorleans/" target="_blank">Geodata</a>
            </p>
        </div>
        
        <div class="footer">
            <p>
                This is an automated message from the OSUC Digital Twin system.<br>
                Please do not reply directly to this email.
            </p>
        </div>
    </body>
    </html>
    """
    return html_body

def email(subject, body, to=EMAIL_HOST_USER, attachments=None, html=False):
    msg = MIMEMultipart()
    if html:
        msg.attach(MIMEText(body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))
    msg["Subject"] = subject
    msg["From"] = EMAIL_HOST_USER
    msg["To"] = to

    if attachments:
        for file in attachments:
            if not os.path.isfile(file):
                log_error(f"--MAIL-- Attachment file {file} not found.")
                continue
            date = datetime.now(tz=timezone.utc).strftime("%Y_%m_%d")
            filename = f"{os.path.basename(file)[:-4]}_{date}.csv"
            with open(file, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={filename}")
                msg.attach(part)
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls() if EMAIL_USE_TLS else server.startssl()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(msg)
            log_info("--MAIL-- Email sent successfully.")
            return True
    except Exception as e:
        log_error(f"--MAIL-- {e}")
        return False

def send_data_email(to=EMAIL_HOST_USER, recipient_name=None, archive=True, return_sent=False):
    """
    Send an email with the latest data file attached.
    """
    subject = "OSUC Digital Twin Data Harvested"
    message = """
        Please find attached the latest data harvested by the OSUC Digital Twin system.
        If you have any questions, please don't hesitate to contact us.
        Feel free to report any issues.
    """
    body = create_html_body(subject, message, recipient_name=recipient_name)
    data_file = f"{BASE_DIR}/db/data.csv"
    sent = email(subject, body, to=to, attachments=[data_file], html=True)

    if sent and archive:
        archive(keep=3)

    if return_sent:
        return sent

def send_data_email_to_many(recipients=EMAIL_RECIPIENTS):
    """
    Send an email with the latest data file attached to multiple recipients.
    """
    all_sent = False
    for recipient in recipients:
        name = str(recipient).split("@")[0].replace(".", " ").title()
        sent = send_data_email(to=recipient.strip(), recipient_name=name, archive=False, return_sent=True)
        all_sent = all_sent or sent
    
    log_info(f"--MAIL-- Emails sent to {len(recipients)} recipients.")

    if all_sent:
        archive(keep=3)

def send_error_email(error_message, subject=None, to=EMAIL_HOST_USER, recipient_name=None):
    """
    Send an email notifying about an error.
    """
    subject = subject if subject else "OSUC Digital Twin System Error Notification"
    message = f"""
        An error occurred in the OSUC Digital Twin system:
        {error_message}
        Please investigate the issue as soon as possible.
    """
    body = create_html_body(subject, message, recipient_name=recipient_name)
    email(subject, body, to=to, html=True)
