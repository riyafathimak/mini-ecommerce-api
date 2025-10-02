import imaplib
import email
from email.header import decode_header
from django.conf import settings
from tracker.models import Client, Ticket

# ----- CONFIG -----
EMAIL_ADDRESS = getattr(settings, "EMAIL_ADDRESS", "riyafathimak7971@gmail.com")
EMAIL_APP_PASSWORD = getattr(settings, "EMAIL_APP_PASSWORD", "bpzrsodzbdckbagz") 
IMAP_SERVER = getattr(settings, "EMAIL_IMAP_SERVER", "imap.gmail.com")


# ----- FETCH EMAILS FUNCTION -----
def fetch_emails():
    try:
        # Connect to the mailbox
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        mail.select("inbox")

        # Search for unseen (unread) emails
        status, messages = mail.search(None, '(UNSEEN)')
        if status != "OK":
            print("No new messages found.")
            return

        for num in messages[0].split():
            status, msg_data = mail.fetch(num, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Decode subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")

            # Get sender email
            from_email = email.utils.parseaddr(msg.get("From"))[1]

            # Get plain text body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                        except Exception:
                            continue
            else:
                try:
                    body = msg.get_payload(decode=True).decode(errors="ignore")
                except Exception:
                    body = "Unable to decode email content."

            # Create or fetch client
            client, _ = Client.objects.get_or_create(
                email=from_email,
                defaults={"name": from_email.split("@")[0]}
            )

            # Create ticket
            Ticket.objects.create(
                title=subject or "No Subject",
                description=body.strip() or "No Content",
                client=client,
                status="New",
                priority="Medium"
            )

            # Mark email as seen
            mail.store(num, '+FLAGS', '\\Seen')

        mail.logout()
        print("✅ Emails fetched and converted to tickets successfully!")

    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP Error: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected Error: {e}")
