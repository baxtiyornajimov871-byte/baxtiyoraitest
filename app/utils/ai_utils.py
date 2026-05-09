"""
BaxtiyorAiTest - AI Utilities
Token counting, context management, and prompt optimization
"""

import re
from typing import List, Dict


def estimate_tokens(text: str) -> int:
    """Rough token estimation (works for most models)"""
    if not text:
        return 0
    # Simple approximation: ~4 characters per token
    return len(text) // 4 + 1


def count_tokens(text: str) -> int:
    """More accurate token counter"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Split by words and punctuation
    words = re.findall(r'\b\w+\b|[^\w\s]', text)
    return len(words) + len(text) // 6  # Bonus for punctuation and structure


def trim_conversation_history(history: List[Dict], max_tokens: int = 4000) -> List[Dict]:
    """Smart trimming of conversation history to fit token limit"""
    if not history:
        return []
    
    total_tokens = 0
    trimmed = []
    
    # Keep system prompt if exists
    if history and history[0].get('role') == 'system':
        system_msg = history[0]
        total_tokens += estimate_tokens(system_msg['content'])
        trimmed.append(system_msg)
        history = history[1:]
    
    # Add messages from newest to oldest until token limit
    for msg in reversed(history):
        msg_tokens = estimate_tokens(msg['content']) + 10  # overhead
        if total_tokens + msg_tokens > max_tokens:
            break
        trimmed.insert(0, msg)  # insert at beginning
        total_tokens += msg_tokens
    
    return trimmed


def build_system_prompt(bot=None, custom_instructions: str = None) -> str:
    """Build rich system prompt"""
    base_prompt = """You are a helpful, creative, and intelligent AI assistant.
You provide clear, accurate, and engaging responses.
Use markdown formatting when appropriate.
Be concise but thorough."""

    if bot:
        base_prompt = f"""You are {bot.name}, created by {bot.owner.display_name if bot.owner else 'a user'}.
{bot.description}

Core Instructions:
{bot.system_prompt}

Personality: Friendly, helpful, and engaging.
"""

    if custom_instructions:
        base_prompt += f"\n\nAdditional Instructions:\n{custom_instructions}"

    return base_prompt.strip()


def optimize_prompt_for_model(prompt: str, model: str) -> str:
    """Model-specific prompt optimization"""
    if "llama" in model.lower():
        return prompt  # Llama models work well with natural language
    elif "mistral" in model.lower():
        return prompt + "\n\nAnswer concisely."
    return prompt


def extract_code_blocks(text: str) -> List[str]:
    """Extract code blocks from markdown response"""
    pattern = r'```(?:\w+)?\n(.*?)\n```'
    return re.findall(pattern, text, re.DOTALL)


def is_safe_prompt(prompt: str) -> bool:
    """Basic safety check for harmful prompts"""
    dangerous_patterns = [
        r'(?i)ignore previous instructions',
        r'(?i)you are now',
        r'(?i)jailbreak',
        r'(?i)dan mode'
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, prompt):
            return False
    return True