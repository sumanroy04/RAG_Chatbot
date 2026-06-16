from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

try:
    from langchain_classic.chains import ConversationalRetrievalChain
    from langchain_classic.memory import ConversationBufferMemory
except ImportError:
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory

from backend.app.config import GROQ_API_KEY
from backend.app.constants import (
    MOOD_PROFILES,
    TOPIC_PROFILES,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_NEGATIVE_PROMPT,
)

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

def chat_chain(
    vectorstore,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    negative_prompt: str = DEFAULT_NEGATIVE_PROMPT,
    selected_mood: str | None = None,
    selected_topic: str | None = None,
):
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.2, groq_api_key=GROQ_API_KEY)

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
