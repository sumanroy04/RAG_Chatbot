def send_email(to_address: str, subject: str, body: str) -> bool:
    """Mock sending an email for notifications/reminders."""
    print(f"[EmailService] Sending email to: {to_address}")
    print(f"[EmailService] Subject: {subject}")
    print(f"[EmailService] Body: {body}")
    return True
