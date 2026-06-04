"""Streamlit UI entry point. Run with: streamlit run streamlit_app.py"""
import os
from datetime import datetime

import streamlit as st
from fpdf import FPDF

from main import (
    GROQ_API_KEY,
    chat_chain,
    remove_emojis,
    setup_vectorstore,
    working_dir,
)

st.set_page_config(
    page_title="PATRONUS",
    page_icon="🧠",
    layout="wide",
)

st.markdown("""
    <style>
    div.css-textbarboxtype {
        background-color: #;
        border: 1px solid #DCDCDC;
        padding: 20px 20px 20px 70px;
        padding: 5% 5% 5% 10%;
        border-radius: 10px;
    }
    div.css-textbarboxtype:nth-of-type(3) {
        text-align: justify;
        text-justify: inter-word;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("About Bot")
    st.markdown("## Description")
    st.markdown("""
        <div class="css-textbarboxtype">
            An AI-powered chatbot designed to provide mental health support.
        </div>
    """, unsafe_allow_html=True)
    st.markdown("## Goals")
    st.markdown("""
        <div class="css-textbarboxtype">
            - Provide 24/7 mental health support<br>
            - Offer crisis intervention when needed<br>
            - Connect users with professional resources
        </div>
    """, unsafe_allow_html=True)
    st.markdown("## Purpose")
    st.markdown("""
        <div class="css-textbarboxtype">
            Designed as a stigma-free entry point to mental health support in India—where people often feel too shy to seek traditional therapy—this chatbot tackles interpersonal harassment, workplace stress, and suicidal ideation by offering empathetic listening, practical coping strategies, and evidence-based guidance from the WHO and India's Ministry of Health and Family Welfare. By normalizing conversations about emotional well-being and delivering timely, trustworthy advice, it bridges users to professional therapists when they're ready.
        </div>
    """, unsafe_allow_html=True)
    st.markdown("## Our Values")
    st.markdown("""
        <div class="css-textbarboxtype">
            - Empathy<br>
            - Professional Ethics<br>
            - User Safety
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("## Chat History")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for idx, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            if st.button(f"Chat {idx//2 + 1}: {message['content'][:30]}...", key=f"history_{idx}"):
                st.session_state.selected_chat = idx // 2
    st.markdown("---")
    if st.button("Export Chat to PDF"):
        if len(st.session_state.chat_history) > 0:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "", 10)
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "Mental Health Chatbot - Conversation History", ln=True, align="C")
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
                pdf.ln(10)
                pdf.set_font("Arial", "", 10)
                for message in st.session_state.chat_history:
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(0, 10, message["role"].capitalize(), ln=True)
                    pdf.set_font("Arial", "", 10)
                    pdf.multi_cell(0, 10, remove_emojis(message["content"]))
                    pdf.ln(5)
                filename = f"mental_health_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                pdf.output(filename)
                with open(filename, "rb") as f:
                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name=filename,
                        mime="application/pdf",
                    )
                os.remove(filename)
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
        else:
            st.warning("No chat history to export!")

st.title("🧠 Mental Health Chatbot")

if not GROQ_API_KEY:
    st.error(
        "Missing Groq API key. Add `GROQ_API_KEY` to `.env` or `config.json` "
        "(see `config.example.json`), from [console.groq.com](https://console.groq.com)."
    )

banner_path = os.path.join(
    working_dir,
    "images",
    "may-is-mental-health-awareness-month-diversity-silhouettes-of-adults-and-children-of-different-nationalities-and-appearances-colorful-people-contour-in-flat-style-vector-2.jpg",
)
if os.path.exists(banner_path):
    st.image(banner_path)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "vectorstore" not in st.session_state:
    with st.spinner("Loading mental health knowledge base..."):
        st.session_state.vectorstore = setup_vectorstore()

if GROQ_API_KEY and "conversational_chain" not in st.session_state:
    st.session_state.conversational_chain = chat_chain(st.session_state.vectorstore)

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask a question about Mental Health")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        if not GROQ_API_KEY:
            assistant_response = (
                "Groq API key is not configured. Add your key to `.env` or `config.json` "
                "and refresh this page."
            )
        else:
            if "conversational_chain" not in st.session_state:
                st.session_state.conversational_chain = chat_chain(st.session_state.vectorstore)
            response = st.session_state.conversational_chain({"question": user_input})
            assistant_response = response["answer"]
        st.markdown(assistant_response)
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
