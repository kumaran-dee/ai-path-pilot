import os
import smtplib
from email.message import EmailMessage
from twilio.rest import Client

class NotificationService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USERNAME")
        self.smtp_pass = os.getenv("SMTP_PASSWORD")
        
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if self.twilio_sid and self.twilio_token:
            self.twilio_client = Client(self.twilio_sid, self.twilio_token)
        else:
            self.twilio_client = None

    def send_email(self, to_email, subject, body):
        if not self.smtp_user or not self.smtp_pass:
            print("SMTP credentials not configured. Skipping email.")
            return False
            
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = to_email

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def send_whatsapp(self, to_number, body):
        if not self.twilio_client:
            print("Twilio credentials not configured. Skipping WhatsApp.")
            return False
            
        try:
            message = self.twilio_client.messages.create(
                body=body,
                from_=f"whatsapp:{self.twilio_number}",
                to=f"whatsapp:{to_number}"
            )
            return message.sid is not None
        except Exception as e:
            print(f"Failed to send WhatsApp: {e}")
            return False

notification_service = NotificationService()
