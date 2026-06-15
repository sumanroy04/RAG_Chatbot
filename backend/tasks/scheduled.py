import time
from backend.services.email import send_email

def send_appointment_reminder(email: str, therapist_name: str, date_time: str):
    """Sends background email reminder for upcoming appointments."""
    time.sleep(1) # simulate delay
    send_email(
        to_address=email,
        subject="Upcoming Appointment Reminder",
        body=f"This is a reminder for your upcoming session with {therapist_name} at {date_time}."
    )
    return True
