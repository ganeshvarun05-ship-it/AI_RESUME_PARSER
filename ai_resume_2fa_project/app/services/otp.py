
import os
import smtplib
from email.message import EmailMessage

def send_email_otp(to_email: str, code: str):
    host = os.getenv("SMTP_HOST")
    if not host:
        # Development mode: code is printed in the terminal.
        print(f"DEV EMAIL OTP for {to_email}: {code}")
        return
    msg = EmailMessage()
    msg["Subject"] = "Your verification code"
    msg["From"] = os.getenv("SMTP_FROM") or os.getenv("SMTP_USERNAME")
    msg["To"] = to_email
    msg.set_content(f"Your verification code is {code}. It expires soon.")
    with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587"))) as server:
        server.starttls()
        server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
        server.send_message(msg)

def send_whatsapp_otp(to_phone: str, code: str):
    # Connect an approved WhatsApp Business provider here.
    # Do not pretend this sends a real WhatsApp message.
    print(f"WHATSAPP PROVIDER NOT CONFIGURED. OTP for {to_phone}: {code}")
