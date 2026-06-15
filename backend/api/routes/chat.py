from fastapi import APIRouter, Request, Depends, HTTPException, status, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.extensions import get_db
from backend.api.models.chat import ChatLog
from backend.api.models.crisis import CrisisLog
from backend.auth.utils import decode_access_token
from backend.chatbot.processor import crisis_matches, get_crisis_response
from backend.chatbot.response import get_llm_reply

chat_router = APIRouter()

class MessageRequest(BaseModel):
    message: str
    mood: str | None = None
    topic: str | None = None

@chat_router.post("/chat")
async def chatbot(
    request: Request,
    body: MessageRequest,
    authorization: str | None = Header(None),
    db: Session = Depends(get_db)
):
    vectorstore = request.app.state.vectorstore
    
    matches = crisis_matches(body.message)
    is_cr = bool(matches)
    
    if is_cr:
        # Retrieve crisis details
        response_text = get_crisis_response(body.mood, body.topic)
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
        user_id = None
        if authorization and authorization.startswith("Bearer "):
            try:
                token = authorization.split(" ")[1]
                payload = decode_access_token(token)
                if payload:
                    user_id = payload.get("user_id")
            except Exception:
                pass
                
        # Log to standard chat history
        log = ChatLog(
            user_id=user_id,
            message=body.message,
            response=response_text,
            mood=body.mood,
            topic=body.topic
        )
        db.add(log)
        
        # If crisis was triggered, also save a detailed crisis event log
        if is_cr:
            matched_str = ", ".join(matches) if matches else "Model Triggered"
            crisis_log = CrisisLog(
                user_id=user_id,
                message=body.message,
                matched_keywords=matched_str
            )
            db.add(crisis_log)
            
        db.commit()
    except Exception:
        pass # Ignore db logging failure
        
    return {
        "response": response_text,
        "is_crisis": is_cr
    }
