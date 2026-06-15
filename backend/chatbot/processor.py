import re

CRISIS_KEYWORDS = [
    "suicide", "suicidal", "suicidal thoughts", "suicidal ideation",
    "kill myself", "end my life", "want to die", "want to disappear",
    "don't want to exist", "do not want to exist", "ending it all",
    "can't go on", "cannot go on", "no reason to live",
    "self-harm", "self harm", "self-injury", "self injury",
    "self mutilation", "self-mutilation", "hurting myself", "harm myself",
    "overdose", "harmful behaviors", "cutting myself",
]

CRISIS_PATTERNS = [
    re.compile(r"\bi\s*(want|need|am going)\s*to\s*(die|kill myself|end my life)\b", re.I),
    re.compile(r"\bi\s*(might|may|will|could)\s*(hurt|harm|kill)\s*myself\b", re.I),
    re.compile(r"\bthinking\s+about\s+(suicide|self[-\s]?harm|ending it all)\b", re.I),
    re.compile(r"\b(plan|planning)\s+to\s+(hurt|harm|kill)\s*myself\b", re.I),
]

_TOPIC_NOTES = {
    "Anxiety": "If this is connected to panic or intense anxiety, try to move near another person or call a helpline while the wave passes.",
    "Sleep Issues": "If the night feels unsafe or overwhelming, please do not stay alone with these thoughts.",
    "Study Stress": "No exam, grade, or deadline is worth your safety. Support matters more than performance right now.",
    "Relationships": "If this is connected to conflict or feeling abandoned, reach out to someone safe before acting on the feeling.",
}

_MOOD_NOTES = {
    "Sad": "Because you marked Sad, I want to say this plainly: your pain deserves care right now.",
    "Stressed": "Because you marked Stressed, focus only on the next safe minute, not the whole problem.",
}

def remove_emojis(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002500-\U00002BEF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d\u23cf\u23e9\u231a\ufe0f\u3030"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text)

def crisis_matches(user_input: str) -> list[str]:
    if not user_input:
        return []
    lowered = user_input.lower()
    matches = [keyword for keyword in CRISIS_KEYWORDS if keyword in lowered]
    matches.extend(pattern.pattern for pattern in CRISIS_PATTERNS if pattern.search(user_input))
    return matches

def is_crisis(user_input: str) -> bool:
    return bool(crisis_matches(user_input))

def get_crisis_response(selected_mood: str | None = None, selected_topic: str | None = None) -> str:
    context_note = _TOPIC_NOTES.get(selected_topic or "") or _MOOD_NOTES.get(selected_mood or "")
    context_note = f"\n\n{context_note}" if context_note else ""

    return (
        "I am really sorry you are feeling this much pain. You are not alone, and you do not "
        "have to handle this by yourself."
        f"{context_note}\n\n"
        "**If you are in immediate danger, please call 112 (National Emergency) right away.**\n\n"
        "Professional mental health resources available in India:\n"
        "- **Tele-MANAS (Govt of India):** 14416 — 24/7, multi-lingual\n"
        "- **KIRAN (Govt Mental Health Rehabilitation):** 1800-599-0019 — 24/7\n"
        "- **Vandrevala Foundation:** 9999 666 555 — 24/7\n"
        "- **iCALL (TISS):** 9152987821 — Mon-Sat, 10 AM-8 PM\n\n"
        "If you can, move away from anything you could use to hurt yourself and contact a trusted "
        "person now. You deserve support and safety."
    )

def get_crisis_html_card(dark_mode: bool = False) -> str:
    bg = "#2b171c" if dark_mode else "#fff4f4"
    border = "#fb7185" if dark_mode else "#f87171"
    left = "#f43f5e" if dark_mode else "#dc2626"
    text = "#fff1f2" if dark_mode else "#1f2937"
    muted = "#fecdd3" if dark_mode else "#4b5563"
    row = "rgba(244,63,94,0.14)" if dark_mode else "rgba(220,38,38,0.05)"

    return f"""
<div class="crisis-card" style="
    background: {bg};
    border: 1px solid {border};
    border-left: 5px solid {left};
    border-radius: 8px;
    padding: 18px 20px;
    margin: 12px 0;
    font-size: 14px;
    line-height: 1.7;
    color: {text};
">
  <div style="font-weight:800; font-size:15px; color:{left}; margin-bottom:8px;">
    🆘 Crisis Support Resources
  </div>
  <p style="margin:0 0 10px; color:{text};">
    You are <strong>not alone</strong>, and help is available.
  </p>
  <p style="margin:0 0 8px; font-weight:700; color:{text};">
    🚨 In immediate danger? Call <span style="color:{left};">112</span>
  </p>
  <table style="width:100%; border-collapse:collapse; font-size:13px; color:{text};">
    <tr><td style="padding:5px 8px 5px 0; font-weight:700;">Tele-MANAS</td><td style="color:{muted};">14416 | 24/7</td></tr>
    <tr style="background:{row};"><td style="padding:5px 8px 5px 0; font-weight:700;">KIRAN</td><td style="color:{muted};">1800-599-0019 | 24/7</td></tr>
    <tr><td style="padding:5px 8px 5px 0; font-weight:700;">Vandrevala</td><td style="color:{muted};">9999 666 555 | 24/7</td></tr>
    <tr style="background:{row};"><td style="padding:5px 8px 5px 0; font-weight:700;">iCALL</td><td style="color:{muted};">9152987821 | Mon-Sat, 10 AM-8 PM</td></tr>
  </table>
</div>
"""
