# crisis.py

# A list of keywords and phrases that trigger the crisis response.
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die",
    "self-harm", "cutting", "hopeless", "no reason to live"
]

def is_crisis(user_input: str) -> bool:
    """
    Analyzes the user's input to determine if it indicates a potential crisis.
    
    Args:
        user_input (str): The raw text input from the user.
        
    Returns:
        bool: True if the input contains crisis-related indicators, False otherwise.
    """
    if not user_input:
        return False
        
    user_input_lower = user_input.lower()
    
    # Check if any keyword exists in the user input
    return any(keyword in user_input_lower for keyword in CRISIS_KEYWORDS)

def get_crisis_response() -> str:
    """
    Returns a standardized, compassionate message with resources.
    """
    # Note: Ensure you update these resources to be appropriate for your 
    # target audience's location (e.g., local emergency hotlines).
    return (
       "I am hearing that you are going through a very difficult time, and I want you to know "
        "that you are not alone. Please consider reaching out to someone who can help.\n\n"
        
        "**If you are in immediate danger, please call 112 (National Emergency Number) right away.**\n\n"
        
        "Here are professional mental health resources available in India:\n"
        "• **Tele-MANAS (Govt of India):** Call 14416 (Available 24/7, multi-lingual support)\n"
        "• **KIRAN (Govt Mental Health Rehabilitation):** 1800-599-0019 (Available 24/7)\n"
        "• **Vandrevala Foundation:** 9999 666 555 (Available 24/7)\n"
        "• **iCALL (TISS):** 9152987821 (Mon-Sat, 10 AM - 8 PM)\n\n"
        
        "These services are free, confidential, and staffed by trained professionals"
    )