def add_calendar_event(title: str, date_time: str, email: str) -> bool:
    """Mock calendar event insert for Google/Outlook Calendar."""
    print(f"[CalendarService] Booking event '{title}' for {email} on {date_time}")
    return True
