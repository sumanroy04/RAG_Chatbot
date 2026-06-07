# main.py
"""
Core logic for Patronus AI: vectorstore setup, LangChain chain, and FastAPI endpoint.
The UI can pass mood/topic button context so responses change based on clicks.
"""

import json
import os
import re

from fastapi import FastAPI
from pydantic import BaseModel

from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

try:
    from langchain_classic.chains import ConversationalRetrievalChain
    from langchain_classic.memory import ConversationBufferMemory
    from langchain_classic.prompts import PromptTemplate
except ImportError:
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory
    from langchain.prompts import PromptTemplate

from crisis import get_crisis_response, is_crisis


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


working_dir = os.path.dirname(os.path.realpath(__file__))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(working_dir, ".env"))
except ImportError:
    pass

config_path = os.path.join(working_dir, "config.json")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip() or os.environ.get("Api_key", "").strip()

if not GROQ_API_KEY and os.path.exists(config_path):
    with open(config_path, encoding="utf-8") as f:
        config_data = json.load(f)
    GROQ_API_KEY = config_data.get("GROQ_API_KEY", "").strip()

if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY


MOOD_PROFILES = {
    "Happy": {"tone": "upbeat and affirming", "ack": "Lovely. I will keep things light and encouraging."},
    "Calm": {"tone": "quiet and grounded", "ack": "Calm mode is on. I will keep the pace steady."},
    "Okay": {"tone": "balanced and gentle", "ack": "Okay is a real place to start. I will help you sort things gently."},
    "Sad": {"tone": "warm and validating", "ack": "I hear you. I will keep my replies soft and manageable."},
    "Stressed": {"tone": "calming and practical", "ack": "Stress mode is on. I will focus on grounding and practical next steps."},
}

TOPIC_PROFILES = {
    "Study Stress": {
        "focus": "academic pressure, exams, procrastination, focus, burnout, and study planning",
        "retrieval_k": 4,
        "starter": "I'd like to talk about study stress and how to handle academic pressure.",
    },
    "Sleep Issues": {
        "focus": "sleep hygiene, racing thoughts at night, routines, rest, and fatigue",
        "retrieval_k": 4,
        "starter": "I'd like to talk about sleep issues and how to rest better.",
    },
    "Relationships": {
        "focus": "relationships, communication, loneliness, conflict, boundaries, and support systems",
        "retrieval_k": 4,
        "starter": "I'd like to talk about relationships and emotional boundaries.",
    },
    "Anxiety": {
        "focus": "anxiety, worry, panic, grounding, breathing, and nervous-system regulation",
        "retrieval_k": 5,
        "starter": "I'd like to talk about anxiety and ways to feel more grounded.",
    },
}


DEFAULT_SYSTEM_PROMPT = """You are Patronus AI, a warm mental health companion.

Talk like a caring friend, not like a formal assistant.
Keep replies short, natural, and conversational.
Most replies should be 1-3 sentences.
Do not over-explain unless the user asks for details.
Avoid long bullet lists unless the user asks for steps.
Use simple language.
Sound emotionally present, gentle, and human.

Your style:
- Validate the user's feeling first.
- Reply like a friend texting back.
- Ask at most one gentle follow-up question.
- Keep the conversation going naturally.
- Use emojis lightly, only when they feel natural.

Examples:
User: "I feel stressed"
Assistant: "That sounds heavy. Take a slow breath with me for a second — what’s been stressing you the most today?"

User: "I can't sleep"
Assistant: "Ugh, that restless feeling is so frustrating. Is your mind racing, or does your body just not feel sleepy?"

User: "I feel sad"
Assistant: "I’m sorry you’re feeling that way. I’m here with you — did something happen today, or has it been building up?"

Important:
- Do not diagnose.
- Do not prescribe medicine.
- Do not pretend to be a therapist.
- If the user may be in danger or talks about self-harm, respond seriously and guide them to immediate support.
"""

DEFAULT_NEGATIVE_PROMPT = """Do not sound robotic, clinical, or lecture-like.
Do not give long explanations by default.
Do not dump bullet points unless asked.
Do not say "based on the provided context" to the user.
Do not mention retrieved documents or databases.
Do not answer unrelated topics in detail.
Do not diagnose, prescribe, or give dangerous advice."""

def get_mood_profile(selected_mood: str | None) -> dict | None:
    return MOOD_PROFILES.get((selected_mood or "").strip())


def get_topic_profile(selected_topic: str | None) -> dict | None:
    return TOPIC_PROFILES.get((selected_topic or "").strip())


def get_mood_acknowledgement(selected_mood: str | None) -> str:
    profile = get_mood_profile(selected_mood)
    return profile["ack"] if profile else "Choose a mood to tune the assistant's tone."


def get_button_starter(selected_topic: str, selected_mood: str | None = None) -> str:
    profile = get_topic_profile(selected_topic)
    starter = profile["starter"] if profile else f"I'd like to talk about {selected_topic.lower()}."
    if selected_mood:
        return f"{starter} I'm feeling {selected_mood.lower()} today."
    return starter


def get_retrieval_k(selected_topic: str | None = None) -> int:
    profile = get_topic_profile(selected_topic)
    return int(profile.get("retrieval_k", 3)) if profile else 3


def build_contextual_system_prompt(
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    selected_mood: str | None = None,
    selected_topic: str | None = None,
) -> str:
    parts = [system_prompt]

    mood_profile = get_mood_profile(selected_mood)
    if mood_profile:
        parts.append(f"User selected mood: {selected_mood}. Use a {mood_profile['tone']} tone.")

    topic_profile = get_topic_profile(selected_topic)
    if topic_profile:
        parts.append(f"User selected topic: {selected_topic}. Focus on {topic_profile['focus']}.")

    return "\n\n".join(parts)


def build_contextual_question(
    message: str,
    selected_mood: str | None = None,
    selected_topic: str | None = None,
) -> str:
    context = []
    if selected_mood:
        context.append(f"Mood button selected: {selected_mood}")
    if selected_topic:
        profile = get_topic_profile(selected_topic)
        focus = profile["focus"] if profile else selected_topic
        context.append(f"Topic button selected: {selected_topic} ({focus})")

    if not context:
        return message

    return "\n".join(["Button context:", *context, "", f"User message: {message}"])


def setup_vectorstore():
    persist_directory = os.path.join(working_dir, "vector_db_dir")
    embeddings = HuggingFaceEmbeddings()
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)


def chat_chain(
    vectorstore,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    negative_prompt: str = DEFAULT_NEGATIVE_PROMPT,
    selected_mood: str | None = None,
    selected_topic: str | None = None,
):
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.6)

    prompt_template = f"""{build_contextual_system_prompt(system_prompt, selected_mood, selected_topic)}

{negative_prompt}

Context from mental health database:
{{context}}

Chat History:
{{chat_history}}

Question:
{{question}}

Answer:"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "chat_history", "question"],
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": get_retrieval_k(selected_topic)})

    memory = ConversationBufferMemory(
        llm=llm,
        output_key="answer",
        memory_key="chat_history",
        return_messages=True,
    )

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        memory=memory,
        verbose=True,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt},
    )


app = FastAPI(title="Patronus AI", description="Mental health support chatbot API")


class MessageRequest(BaseModel):
    message: str
    mood: str | None = None
    topic: str | None = None


@app.post("/chat")
async def chatbot(request: MessageRequest):
    if is_crisis(request.message):
        return {
            "response": get_crisis_response(),
            "is_crisis": True,
        }

    vectorstore = setup_vectorstore()
    conversational_chain = chat_chain(
        vectorstore,
        selected_mood=request.mood,
        selected_topic=request.topic,
    )

    contextual_question = build_contextual_question(
        request.message,
        selected_mood=request.mood,
        selected_topic=request.topic,
    )

    response = conversational_chain({"question": contextual_question})["answer"]

    return {
        "response": response,
        "is_crisis": False,
    }