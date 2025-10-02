import imaplib
import email
from email.header import decode_header
from .models import Email  # your Email model

def fetch_gmail_emails():
    username = "your_email@gmail.com"
    password = "your_app_password"

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")

    status, messages = mail.search(None, "ALL")
    mail_ids = messages[0].split()

    for mail_id in mail_ids[-5:]:  # last 5 emails
        status, msg_data = mail.fetch(mail_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")
                from_ = msg.get("From")
                body = msg.get_payload(decode=True).decode()
                # Save to DB
                Email.objects.create(sender=from_, subject=subject, body=body)
