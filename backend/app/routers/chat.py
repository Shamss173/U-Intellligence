"""
Chat router
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.models.conversation import Conversation, Message
from app.services.rag_service import rag_service
from app.services.title_generator import TitleGenerator
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    department_id: str
    message: str
    conversation_id: Optional[int] = None
    memory_enabled: bool = True


class ChatResponse(BaseModel):
    conversation_id: int
    message: str
    timestamp: datetime


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Handle chat messages with RAG integration
    """
    try:
        # Get or create conversation
        if request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id
            ).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            # Create new conversation
            conversation = Conversation(
                department_id=request.department_id,
                memory_enabled=request.memory_enabled
            )
            db.add(conversation)
            db.flush()  # Get the ID
        
        # Update memory setting if changed
        conversation.memory_enabled = request.memory_enabled
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        
        # Generate title if this is the first message
        if not conversation.title:
            conversation.title = TitleGenerator.generate_title(request.message)
        
        # Get conversation context if memory is enabled
        context = None
        if request.memory_enabled:
            previous_messages = db.query(Message).filter(
                Message.conversation_id == conversation.id
            ).order_by(Message.timestamp.asc()).all()
            context = [
                {"role": msg.role, "content": msg.content}
                for msg in previous_messages
            ]
        
        # Query RAG service for response
        logger.debug(f"Calling RAG service for department: {request.department_id}")
        assistant_response = await rag_service.query(
            department_id=request.department_id,
            query=request.message,
            context=context
        )
        
        # Save assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_response
        )
        db.add(assistant_message)
        
        db.commit()
        db.refresh(assistant_message)
        
        return ChatResponse(
            conversation_id=conversation.id,
            message=assistant_response,
            timestamp=assistant_message.timestamp
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{conversation_id}/messages", response_model=List[ChatMessage])
async def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    """Get all messages for a conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp.asc()).all()
    
    return [
        ChatMessage(
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp
        )
        for msg in messages
    ]

