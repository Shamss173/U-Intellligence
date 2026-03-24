"""
Title Generator Service
Generates conversation titles from user prompts
"""
import re
from typing import Optional


class TitleGenerator:
    """Service for generating conversation titles"""
    
    @staticmethod
    def generate_title(user_prompt: str, max_length: int = 50) -> str:
        """
        Generate a title from user prompt
        
        Args:
            user_prompt: The first user message in the conversation
            max_length: Maximum title length
        
        Returns:
            str: Generated title
        """
        if not user_prompt:
            return "New Conversation"
        
        # Clean the prompt
        title = user_prompt.strip()
        
        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title)
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()
        
        # Truncate if too long
        if len(title) > max_length:
            title = title[:max_length - 3] + "..."
        
        return title if title else "New Conversation"
    
    @staticmethod
    def generate_title_from_messages(messages: list, max_length: int = 50) -> str:
        """
        Generate title from conversation messages
        
        Args:
            messages: List of message objects
            max_length: Maximum title length
        
        Returns:
            str: Generated title
        """
        if not messages:
            return "New Conversation"
        
        # Find first user message
        for msg in messages:
            if hasattr(msg, 'role') and msg.role == 'user':
                if hasattr(msg, 'content'):
                    return TitleGenerator.generate_title(msg.content, max_length)
            elif isinstance(msg, dict) and msg.get('role') == 'user':
                return TitleGenerator.generate_title(msg.get('content', ''), max_length)
        
        return "New Conversation"

