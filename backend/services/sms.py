def send_sms(message: str) -> bool:
    """Mock sending SMS message via Twilio or other provider."""
    print(f"[SMSService] Sending SMS text message: {message}")
    return True
