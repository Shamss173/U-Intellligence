"""
Conversations router
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.conversation import Conversation, Message
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class ConversationSummary(BaseModel):
    id: int
    department_id: str
    title: str
    memory_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime]
    message_count: int


@router.get("/{department_id}", response_model=List[ConversationSummary])
async def get_conversations(
    department_id: str,
    db: Session = Depends(get_db)
):
    """Get all conversations for a department"""
    conversations = db.query(Conversation).filter(
        Conversation.department_id == department_id
    ).order_by(Conversation.created_at.desc()).all()
    
    result = []
    for conv in conversations:
        message_count = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).count()
        
        result.append(ConversationSummary(
            id=conv.id,
            department_id=conv.department_id,
            title=conv.title or "Untitled Conversation",
            memory_enabled=conv.memory_enabled,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=message_count
        ))
    
    return result


@router.get("/detail/{conversation_id}")
async def get_conversation_detail(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed conversation information"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp.asc()).all()
    
    return {
        "id": conversation.id,
        "department_id": conversation.department_id,
        "title": conversation.title,
        "memory_enabled": conversation.memory_enabled,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in messages
        ]
    }


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted successfully"}


@router.patch("/{conversation_id}/memory")
async def toggle_memory(
    conversation_id: int,
    memory_enabled: bool = Query(...),
    db: Session = Depends(get_db)
):
    """Toggle memory for a conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation.memory_enabled = memory_enabled
    db.commit()
    db.refresh(conversation)
    
    return {
        "id": conversation.id,
        "memory_enabled": conversation.memory_enabled
    }

