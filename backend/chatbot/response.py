from backend.app.config import GROQ_API_KEY
from backend.chatbot.processor import is_crisis, get_crisis_response
from backend.chatbot.rag_engine import chat_chain, build_contextual_question

def get_llm_reply(
    vectorstore,
    user_input: str,
    selected_mood: str | None = None,
    selected_topic: str | None = None
) -> tuple[str, bool]:
    """Retrieves context and queries LLM via RAG chain, returning (response, is_crisis)."""
    
    if is_crisis(user_input):
        return get_crisis_response(selected_mood, selected_topic), True

    if not GROQ_API_KEY:
        return "Groq API key not configured. Please add GROQ_API_KEY to your env variables.", False

    if vectorstore is None:
        return "Vector database is not initialized. Please load documents first.", False

    try:
        conversational_chain = chat_chain(
            vectorstore,
            selected_mood=selected_mood,
            selected_topic=selected_topic,
        )
        contextual_question = build_contextual_question(
            user_input,
            selected_mood=selected_mood,
            selected_topic=selected_topic,
        )
        
        result = conversational_chain({"question": contextual_question})
        return result["answer"], False
    except Exception as exc:
        return f"An error occurred while generating response: {exc}", False

