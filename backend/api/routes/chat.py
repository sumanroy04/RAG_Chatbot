from fastapi import APIRouter, Request, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.extensions import get_db
from backend.api.models.chat import ChatLog
from backend.chatbot.processor import is_crisis, get_crisis_response
from backend.chatbot.response import get_llm_reply

chat_router = APIRouter()

class MessageRequest(BaseModel):
    message: str
    mood: str | None = None
    topic: str | None = None

@chat_router.post("/chat")
async def chatbot(request: Request, body: MessageRequest, db: Session = Depends(get_db)):
    vectorstore = request.app.state.vectorstore
    
    if is_crisis(body.message):
        # Retrieve crisis details
        response_text = get_crisis_response(body.mood, body.topic)
        is_cr = True
    else:
        # Generate chatbot reply using vectorstore and Groq LLM
        response_text, is_cr = get_llm_reply(
            vectorstore=vectorstore,
            user_input=body.message,
            selected_mood=body.mood,
            selected_topic=body.topic
        )
        
    # Log interactions in the DB
    try:
        log = ChatLog(
            message=body.message,
            response=response_text,
            mood=body.mood,
            topic=body.topic
        )
        db.add(log)
        db.commit()
    except Exception:
        pass # Ignore db logging failure
        
    return {
        "response": response_text,
        "is_crisis": is_cr
    }
