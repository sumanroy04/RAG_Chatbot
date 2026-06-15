"""
Patronus AI — Streamlit UI.
Run with: streamlit run backend/streamlit_app.py
"""

import base64
import html
import mimetypes
import os
import sys
import re
from datetime import datetime
from pathlib import Path

import streamlit as st

# Setup system path to backend parent to import packages
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir.parent))

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

try:
    from backend.app.config import GROQ_API_KEY
    from backend.chatbot.rag_engine import (
        build_contextual_question,
        chat_chain,
        get_button_starter,
        get_mood_acknowledgement,
    )
    from backend.chatbot.processor import (
        remove_emojis,
        is_crisis,
        get_crisis_response,
        get_crisis_html_card,
    )
    from backend.chatbot.knowledge_base import setup_vectorstore
    working_dir = str(backend_dir)
    MAIN_IMPORT_ERROR = None
except Exception as exc:
    MAIN_IMPORT_ERROR = exc
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    working_dir = os.path.dirname(os.path.abspath(__file__))

    def setup_vectorstore(): return None
    def chat_chain(vs, **kwargs): return None
    def remove_emojis(text): return text
    def build_contextual_question(message, selected_mood=None, selected_topic=None): return message
    def get_button_starter(topic, selected_mood=None): return f"I'd like to talk about {topic.lower()}."
    def get_mood_acknowledgement(selected_mood=None): return "Choose a mood to tune the assistant's tone."
    def is_crisis(text): return False
    def get_crisis_response(selected_mood=None, selected_topic=None): return ""
    def get_crisis_html_card(dark_mode=False): return ""


st.set_page_config(
    page_title="Patronus AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def image_to_data_uri(file_name: str) -> str:
    # Use images folder under data-storage
    path = os.path.join(working_dir, "..", "data-storage", "images", file_name)
    if not os.path.exists(path):
        return ""
    mime_type = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


HERO_IMAGE_URI = ""
for candidate in [
    "may-is-mental-health-awareness-month-diversity-silhouettes-of-adults-and-children-of-different-nationalities-and-appearances-colorful-people-contour-in-flat-style-vector-2.jpg",
    "Panromic_May_Is_Mental_HEALTH_Awareness_Month_image.png",
    "banner-for-mental-health-awareness-month-in-may.jpg",
]:
    HERO_IMAGE_URI = image_to_data_uri(candidate)
    if HERO_IMAGE_URI:
        break


for key, default in {
    "chat_history": [],
    "selected_mood": None,
    "selected_topic": None,
    "vectorstore": None,
    "conversational_chain": None,
    "chain_signature": None,
    "kb_error": None,
    "dark_mode": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


LIGHT_THEME = {
    "app_bg": "linear-gradient(135deg, #eef4ff 0%, #f4edff 46%, #fff3f7 100%)",
    "sidebar_bg": "#eef3fb",
    "surface": "#ffffff",
    "surface_soft": "#f7f4ff",
    "surface_hover": "#f1edff",
    "text": "#141827",
    "muted": "#667085",
    "border": "rgba(20,24,39,0.10)",
    "accent": "#7357f6",
    "accent_hover": "#6146df",
    "accent_soft": "#ece7ff",
    "accent_text": "#4f35c7",
    "chat_bg": "rgba(255,255,255,0.66)",
    "shadow": "0 18px 45px rgba(104, 93, 151, 0.14)",
    "button_shadow": "0 10px 22px rgba(115, 87, 246, 0.24)",
}

DARK_THEME = {
    "app_bg": "linear-gradient(135deg, #0f1320 0%, #171527 48%, #241827 100%)",
    "sidebar_bg": "#121826",
    "surface": "#1d2433",
    "surface_soft": "#242b3b",
    "surface_hover": "#2d3548",
    "text": "#f7f3ff",
    "muted": "#c9c5d8",
    "border": "rgba(255,255,255,0.13)",
    "accent": "#9b8cff",
    "accent_hover": "#b0a5ff",
    "accent_soft": "#302e57",
    "accent_text": "#f1edff",
    "chat_bg": "rgba(18,24,38,0.76)",
    "shadow": "0 18px 48px rgba(0,0,0,0.35)",
    "button_shadow": "0 10px 25px rgba(155, 140, 255, 0.22)",
}

theme = DARK_THEME if st.session_state.dark_mode else LIGHT_THEME
css_vars = "\n".join(
    f"    --pat-{name.replace('_', '-')}: {value};"
    for name, value in theme.items()
)
hero_var = f'    --pat-hero-image: url("{HERO_IMAGE_URI}");' if HERO_IMAGE_URI else "    --pat-hero-image: none;"


st.markdown(
    """
<style>
:root {
__CSS_VARS__
__HERO_VAR__
}

#MainMenu, footer, header { visibility: hidden; }

html, body, .stApp, [class*="css"] {
    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

.stApp {
    background: var(--pat-app-bg) !important;
    color: var(--pat-text) !important;
}

.block-container {
    padding: 2rem 2.25rem 1rem !important;
    max-width: 100% !important;
}

.stMarkdown, [data-testid="stMarkdownContainer"], p, h1, h2, h3, h4, label {
    color: var(--pat-text) !important;
    letter-spacing: 0 !important;
}

[data-testid="stSidebar"] {
    background: var(--pat-sidebar-bg) !important;
    border-right: 1px solid var(--pat-border);
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1.65rem 1.2rem 1rem;
}

.brand-row {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    font-size: 1.65rem;
    font-weight: 800;
    color: var(--pat-text);
    margin-bottom: 1.05rem;
}

.brand-mark {
    width: 28px;
    height: 28px;
    display: grid;
    place-items: center;
    border-radius: 8px;
    background: linear-gradient(135deg, #ffa7c4, #f3d1ff);
}

.sidebar-label {
    font-weight: 600;
    color: var(--pat-text);
    margin: 1.1rem 0 0.35rem;
}

.about-card, .status-card {
    background: var(--pat-surface);
    border: 1px solid var(--pat-border);
    border-radius: 8px;
    padding: 1rem;
    box-shadow: var(--pat-shadow);
}

.about-card strong, .status-card strong {
    display: block;
    margin-bottom: 0.35rem;
    font-size: 1rem;
    color: var(--pat-text);
}

.about-card p, .status-card p {
    margin: 0;
    color: var(--pat-muted) !important;
    line-height: 1.55;
    font-size: 0.9rem;
}

.sb-divider {
    border: none;
    border-top: 1px solid var(--pat-border);
    margin: 0.75rem 0;
}

button {
    transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease, border-color 160ms ease !important;
}

button:hover { transform: translateY(-2px); }
button:active { transform: translateY(0) scale(0.97); }

div.new-chat-btn > div > button {
    background: var(--pat-accent) !important;
    color: white !important;
    border: 0 !important;
    border-radius: 8px !important;
    min-height: 3.25rem !important;
    font-weight: 700 !important;
    box-shadow: var(--pat-button-shadow) !important;
}

div.new-chat-btn > div > button:hover {
    background: var(--pat-accent-hover) !important;
}

div.recent-btn > div > button {
    background: var(--pat-surface) !important;
    color: var(--pat-text) !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    min-height: 3.2rem !important;
    justify-content: flex-start !important;
    padding-left: 0.9rem !important;
    font-weight: 500 !important;
}

div.recent-btn > div > button:hover {
    border-color: var(--pat-border) !important;
    box-shadow: var(--pat-shadow) !important;
}

div.mood-btn > div > button,
div.mood-btn-selected > div > button {
    background: var(--pat-surface) !important;
    color: var(--pat-text) !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    min-height: 6.6rem !important;
    font-size: 0.94rem !important;
    font-weight: 600 !important;
    box-shadow: 0 10px 25px rgba(90, 79, 134, 0.10) !important;
    white-space: pre-line !important;
}

div.mood-btn > div > button:hover {
    border-color: var(--pat-accent) !important;
    background: var(--pat-surface-hover) !important;
}

div.mood-btn-selected > div > button {
    background: var(--pat-accent-soft) !important;
    border-color: var(--pat-accent) !important;
    color: var(--pat-accent-text) !important;
}

div.chip-btn > div > button,
div.chip-btn-selected > div > button {
    background: var(--pat-surface) !important;
    color: var(--pat-text) !important;
    border: 1px solid transparent !important;
    border-radius: 999px !important;
    min-height: 2.65rem !important;
    padding: 0 1.05rem !important;
    font-weight: 600 !important;
    box-shadow: 0 8px 22px rgba(90, 79, 134, 0.08) !important;
    white-space: nowrap !important;
}

div.chip-btn > div > button:hover {
    border-color: var(--pat-accent) !important;
    background: var(--pat-surface-hover) !important;
}

div.chip-btn-selected > div > button {
    background: var(--pat-accent-soft) !important;
    border-color: var(--pat-accent) !important;
    color: var(--pat-accent-text) !important;
}

.welcome-header h1 {
    margin: 0;
    font-size: clamp(2rem, 3vw, 3.05rem);
    line-height: 1.02;
    font-weight: 800;
    color: var(--pat-text);
}

.welcome-header p {
    color: var(--pat-muted) !important;
    font-size: 1.05rem;
    margin: 0.55rem 0 0;
}

.theme-hint {
    color: var(--pat-muted);
    text-align: right;
    font-size: 0.78rem;
    margin-top: 0.35rem;
}

.hero-strip {
    min-height: 128px;
    border-radius: 8px;
    border: 1px solid var(--pat-border);
    background-image: linear-gradient(90deg, var(--pat-chat-bg) 0%, var(--pat-chat-bg) 44%, rgba(255,255,255,0.18) 100%), var(--pat-hero-image);
    background-size: cover;
    background-position: center right;
    box-shadow: var(--pat-shadow);
    padding: 1.15rem 1.25rem;
    margin: 0.2rem 0 1.05rem;
    overflow: hidden;
}

.hero-strip h2 {
    margin: 0;
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--pat-text);
}

.hero-strip p {
    max-width: 35rem;
    margin: 0.35rem 0 0;
    color: var(--pat-muted) !important;
    line-height: 1.45;
}

.context-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    margin-top: 0.8rem;
    padding: 0.42rem 0.7rem;
    border-radius: 999px;
    background: var(--pat-surface);
    color: var(--pat-text);
    border: 1px solid var(--pat-border);
    font-weight: 700;
    font-size: 0.82rem;
}

.panel-title {
    margin: 0.85rem 0 0.7rem;
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--pat-text);
}

.context-note {
    margin: 0.8rem 0 0.25rem;
    padding: 0.7rem 0.85rem;
    border-radius: 8px;
    background: var(--pat-surface-soft);
    color: var(--pat-muted);
    border: 1px solid var(--pat-border);
    font-size: 0.92rem;
}

.chat-shell {
    margin-top: 1.1rem;
    min-height: 13rem;
    background: var(--pat-chat-bg);
    border: 1px solid var(--pat-border);
    border-radius: 8px;
    box-shadow: var(--pat-shadow);
    padding: 1.1rem 1.2rem;
    backdrop-filter: blur(18px);
}

.chat-row {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    margin: 0.65rem 0 1rem;
    animation: patFadeUp 220ms ease both;
}

.chat-row.user { justify-content: flex-end; }
.chat-row.user .avatar { order: 2; background: linear-gradient(135deg, #ff6578, #ff8a64); }
.chat-row.assistant .avatar { background: linear-gradient(135deg, #ffca55, #f7a93d); }

.avatar {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    flex: 0 0 auto;
    color: white;
    font-size: 1.05rem;
    box-shadow: 0 8px 18px rgba(0,0,0,0.14);
}

.bubble {
    max-width: min(780px, 78%);
    border-radius: 8px;
    padding: 0.9rem 1rem;
    border: 1px solid var(--pat-border);
    background: var(--pat-surface);
    color: var(--pat-text);
    line-height: 1.62;
}

.chat-row.user .bubble {
    background: var(--pat-surface-soft);
}

.bubble p { margin: 0 0 0.6rem; }
.bubble p:last-child { margin-bottom: 0; }
.bubble ul { margin: 0.25rem 0 0.65rem 1.15rem; }
.bubble li { margin: 0.3rem 0; }

[data-testid="stChatInput"] {
    background: var(--pat-surface) !important;
    border: 1px solid var(--pat-border) !important;
    border-radius: 999px !important;
    box-shadow: var(--pat-shadow) !important;
    padding: 0.35rem 0.55rem !important;
}

[data-testid="stChatInput"] textarea {
    color: var(--pat-text) !important;
    background: transparent !important;
}

[data-testid="stChatInputSubmitButton"] {
    background: var(--pat-accent) !important;
    border-radius: 50% !important;
    border: 0 !important;
    width: 2.2rem !important;
    height: 2.2rem !important;
    min-width: 2.2rem !important;
    min-height: 2.2rem !important;
    padding: 0 !important;
    display: grid !important;
    place-items: center !important;
}

[data-testid="stChatInputSubmitButton"]:hover {
    background: var(--pat-accent-hover) !important;
    transform: scale(1.08) !important;
}

[data-testid="stChatInput"] button[kind="primaryFormSubmit"]:hover {
    background: var(--pat-accent-hover) !important;
    transform: scale(1.08) !important;
}

[data-testid="stChatInput"] button[kind="primaryFormSubmit"]:hover {
    background: var(--pat-accent-hover) !important;
    transform: scale(1.04) !important;
}

@keyframes patFadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 900px) {
    .block-container { padding: 1.1rem 1rem 1rem !important; }
    .hero-strip { min-height: 170px; background-position: center; }
    .bubble { max-width: 88%; }
    .welcome-header h1 { font-size: 2rem; }
}
</style>
""".replace("__CSS_VARS__", css_vars).replace("__HERO_VAR__", hero_var),
    unsafe_allow_html=True,
)


def classed_button(label: str, css_class: str, key: str) -> bool:
    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
    clicked = st.button(label, key=key, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    return clicked


def reset_chain_context():
    st.session_state.conversational_chain = None
    st.session_state.chain_signature = None
    st.session_state.kb_error = None


def ensure_chain(selected_mood: str | None = None, selected_topic: str | None = None):
    if st.session_state.vectorstore is None:
        with st.spinner("Loading knowledge base..."):
            try:
                st.session_state.vectorstore = setup_vectorstore()
            except Exception as exc:
                st.session_state.kb_error = f"Knowledge base load failed: {exc}"
                st.session_state.vectorstore = None
                return

    signature = (selected_mood, selected_topic)
    if GROQ_API_KEY and (
        st.session_state.conversational_chain is None
        or st.session_state.chain_signature != signature
    ):
        try:
            st.session_state.conversational_chain = chat_chain(
                st.session_state.vectorstore,
                selected_mood=selected_mood,
                selected_topic=selected_topic,
            )
            st.session_state.chain_signature = signature
            st.session_state.kb_error = None
        except Exception as exc:
            st.session_state.kb_error = f"Chat chain setup failed: {exc}"
            st.session_state.conversational_chain = None


def get_llm_reply(user_input: str, selected_mood: str | None = None, selected_topic: str | None = None) -> tuple[str, bool]:
    selected_mood = selected_mood or st.session_state.selected_mood
    selected_topic = selected_topic or st.session_state.selected_topic

    if is_crisis(user_input):
        return get_crisis_response(selected_mood, selected_topic), True

    ensure_chain(selected_mood, selected_topic)

    if not GROQ_API_KEY:
        return "Groq API key not configured. Add it to `.env` or `config.json` and refresh.", False

    if MAIN_IMPORT_ERROR is not None:
        return f"App import failed: {MAIN_IMPORT_ERROR}", False

    if st.session_state.kb_error:
        return st.session_state.kb_error, False

    if st.session_state.conversational_chain is None:
        return "Knowledge base did not finish initializing. Check the error shown above.", False

    contextual_question = build_contextual_question(
        user_input,
        selected_mood=selected_mood,
        selected_topic=selected_topic,
    )
    response = st.session_state.conversational_chain({"question": contextual_question})
    return response["answer"], False


def _inline_format(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)


def render_message_text(text: str) -> str:
    escaped = html.escape(text or "")
    lines = escaped.splitlines() or [""]
    parts = []
    in_list = False

    for raw_line in lines:
        line = raw_line.strip()
        bullet = line.startswith(("- ", "* ", "• "))

        if bullet:
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append(f"<li>{_inline_format(line[2:].strip())}</li>")
            continue

        if in_list:
            parts.append("</ul>")
            in_list = False

        if not line:
            parts.append("<br>")
        else:
            parts.append(f"<p>{_inline_format(line)}</p>")

    if in_list:
        parts.append("</ul>")

    return "".join(parts)


def message_to_html(message: dict) -> str:
    role = message.get("role", "assistant")
    icon = "🧑" if role == "user" else "🤖"
    content = render_message_text(message.get("content", ""))

    crisis_html = ""
    if message.get("crisis"):
        crisis_html = get_crisis_html_card(st.session_state.dark_mode)

    return f"""
<div class="chat-row {role}">
    <div class="avatar">{icon}</div>
    <div class="bubble">{content}</div>
</div>
{crisis_html}
"""


def export_chat_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Patronus AI - Conversation History", ln=True, align="C")
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    pdf.ln(6)

    for msg in st.session_state.chat_history:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 8, msg["role"].capitalize(), ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 8, remove_emojis(msg["content"]))
        pdf.ln(3)

    fname = f"patronus_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(fname)

    with open(fname, "rb") as f:
        st.download_button("Download PDF", f, file_name=fname, mime="application/pdf")

    os.remove(fname)


with st.sidebar:
    st.markdown(
        '<div class="brand-row"><span class="brand-mark">🧠</span><span>Patronus AI</span></div>',
        unsafe_allow_html=True,
    )

    if classed_button("+ New Chat", "new-chat-btn", "new_chat"):
        st.session_state.chat_history = []
        st.session_state.selected_mood = None
        st.session_state.selected_topic = None
        reset_chain_context()
        st.rerun()

    st.markdown('<div class="sidebar-label">Recent Chats</div>', unsafe_allow_html=True)

    user_msgs = [m["content"] for m in st.session_state.chat_history if m["role"] == "user"]
    display_chats = user_msgs[-5:][::-1] if user_msgs else ["Exam Stress", "Anxiety Help", "Sleep Issues"]

    for i, chat in enumerate(display_chats):
        label = (chat[:28] + "...") if len(chat) > 28 else chat
        classed_button(label, "recent-btn", f"recent_{i}")

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    mood = st.session_state.selected_mood or "Not selected"
    topic = st.session_state.selected_topic or "Open chat"
    st.markdown(
        f"""
        <div class="status-card">
            <strong>Current Focus</strong>
            <p>Mood: {html.escape(mood)}<br>Topic: {html.escape(topic)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if HAS_FPDF and st.session_state.chat_history:
        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
        if st.button("Export Chat to PDF", use_container_width=True):
            try:
                export_chat_pdf()
            except Exception as exc:
                st.error(f"PDF error: {exc}")

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="about-card">
            <strong>About</strong>
            <p>AI-powered mental wellness assistant designed to provide empathetic support and guidance.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


header_cols = st.columns([9, 1])
with header_cols[0]:
    st.markdown(
        """
        <div class="welcome-header">
            <h1>Welcome Back 👋</h1>
            <p>Your safe space to talk and reflect.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_cols[1]:
    theme_icon = "☀️" if st.session_state.dark_mode else "🌙"
    if st.button(theme_icon, help="Toggle dark mode", key="dark_toggle", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown('<div class="theme-hint">Theme</div>', unsafe_allow_html=True)


if not GROQ_API_KEY:
    st.warning(
        "No Groq API key found. Add `GROQ_API_KEY` to your environment variables or config.json. "
        "Get yours at [console.groq.com](https://console.groq.com).",
        icon="⚠️",
    )


selected_context = []
if st.session_state.selected_mood:
    selected_context.append(st.session_state.selected_mood)
if st.session_state.selected_topic:
    selected_context.append(st.session_state.selected_topic)

context_label = " • ".join(selected_context) if selected_context else "Choose a mood or topic to tune replies"

st.markdown(
    f"""
    <section class="hero-strip">
        <h2>How are you feeling today?</h2>
        <p>Pick a mood to set the tone, then choose a topic chip or write freely. Patronus will adapt the response style and retrieval focus.</p>
        <span class="context-pill">✨ {html.escape(context_label)}</span>
    </section>
    """,
    unsafe_allow_html=True,
)


MOODS = [
    ("😊", "Happy"),
    ("😌", "Calm"),
    ("😐", "Okay"),
    ("😔", "Sad"),
    ("😤", "Stressed"),
]

mood_cols = st.columns(len(MOODS), gap="medium")
for col, (emoji, label) in zip(mood_cols, MOODS):
    with col:
        css_class = "mood-btn-selected" if st.session_state.selected_mood == label else "mood-btn"
        if classed_button(f"{emoji}\n{label}", css_class, f"mood_{label}"):
            st.session_state.selected_mood = label
            reset_chain_context()
            st.rerun()


st.markdown(
    f'<div class="context-note">{html.escape(get_mood_acknowledgement(st.session_state.selected_mood))}</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="panel-title">Choose a focus</div>', unsafe_allow_html=True)

TOPICS = [
    ("📚", "Study Stress"),
    ("😴", "Sleep Issues"),
    ("💖", "Relationships"),
    ("😰", "Anxiety"),
]

chip_cols = st.columns([1.2, 1.2, 1.35, 1.05, 3.2], gap="small")
for i, (icon, topic) in enumerate(TOPICS):
    with chip_cols[i]:
        css_class = "chip-btn-selected" if st.session_state.selected_topic == topic else "chip-btn"
        if classed_button(f"{icon} {topic}", css_class, f"topic_{topic}"):
            st.session_state.selected_topic = topic
            reset_chain_context()

            starter = get_button_starter(topic, st.session_state.selected_mood)
            st.session_state.chat_history.append({
                "role": "user",
                "content": starter,
                "mood": st.session_state.selected_mood,
                "topic": topic,
            })

            reply, crisis = get_llm_reply(starter, st.session_state.selected_mood, topic)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": reply,
                "crisis": crisis,
                "mood": st.session_state.selected_mood,
                "topic": topic,
            })
            st.rerun()


if not st.session_state.chat_history:
    messages_html = message_to_html({
        "role": "assistant",
        "content": "Hello! I'm Patronus AI. What would you like to talk about today?",
    })
else:
    messages_html = "".join(message_to_html(message) for message in st.session_state.chat_history)

st.markdown(f'<div class="chat-shell">{messages_html}</div>', unsafe_allow_html=True)


if user_input := st.chat_input("Share your thoughts..."):
    mood = st.session_state.selected_mood
    topic = st.session_state.selected_topic

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "mood": mood,
        "topic": topic,
    })

    reply, crisis = get_llm_reply(user_input, mood, topic)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": reply,
        "crisis": crisis,
        "mood": mood,
        "topic": topic,
    })

    st.rerun()
