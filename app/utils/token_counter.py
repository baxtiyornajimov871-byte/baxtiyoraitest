"""
BaxtiyorAiTest - Token Counter Utility
Accurate token estimation for different AI models
"""

import re
from typing import List, Dict, Any


class TokenCounter:
    """Advanced Token Counter for cost estimation and context management"""

    # Approximate tokens per character for different models
    MODEL_RATIOS = {
        "llama": 0.25,      # ~4 chars per token
        "mistral": 0.25,
        "gemma": 0.25,
        "mixtral": 0.25,
        "default": 0.25
    }

    @staticmethod
    def count_tokens(text: str, model: str = "llama3-70b-8192") -> int:
        """Count tokens in a text string"""
        if not text:
            return 0

        # Clean text
        text = text.strip()
        
        # Basic tokenization
        words = re.findall(r'\b\w+\b', text)
        punctuation = re.findall(r'[^\w\s]', text)
        
        # Base count
        base_tokens = len(words) + len(punctuation)
        
        # Add overhead for special formatting
        base_tokens += len(text) // 15
        
        # Model-specific adjustment
        model_lower = model.lower()
        ratio = TokenCounter.MODEL_RATIOS.get("llama" if "llama" in model_lower else
                                             "mistral" if "mistral" in model_lower else
                                             "default")
        
        estimated = int(base_tokens / ratio)
        return max(estimated, 1)

    @staticmethod
    def count_messages_tokens(messages: List[Dict[str, Any]], model: str = "llama3-70b-8192") -> int:
        """Count tokens in a list of chat messages"""
        total = 0
        for msg in messages:
            content = msg.get('content', '')
            role_tokens = 4  # role overhead (system, user, assistant)
            content_tokens = TokenCounter.count_tokens(content, model)
            total += content_tokens + role_tokens
        return total

    @staticmethod
    def trim_to_token_limit(messages: List[Dict], max_tokens: int = 6000, 
                           model: str = "llama3-70b-8192") -> List[Dict]:
        """Trim conversation history to stay under token limit"""
        if not messages:
            return []

        total = TokenCounter.count_messages_tokens(messages, model)
        
        if total <= max_tokens:
            return messages

        # Keep system message if present
        system_messages = [m for m in messages if m.get('role') == 'system']
        other_messages = [m for m in messages if m.get('role') != 'system']
        
        trimmed = system_messages.copy()
        current_tokens = TokenCounter.count_messages_tokens(system_messages, model)

        # Add recent messages from the end
        for msg in reversed(other_messages):
            msg_tokens = TokenCounter.count_tokens(msg.get('content', ''), model) + 6
            if current_tokens + msg_tokens > max_tokens:
                break
            trimmed.insert(0, msg)  # Insert at the beginning to keep order
            current_tokens += msg_tokens

        return trimmed

    @staticmethod
    def get_token_usage_summary(messages: List[Dict], response_text: str = "") -> Dict:
        """Generate detailed token usage report"""
        prompt_tokens = TokenCounter.count_messages_tokens(messages)
        completion_tokens = TokenCounter.count_tokens(response_text)
        
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "estimated_cost": round((prompt_tokens * 0.0000005) + (completion_tokens * 0.0000015), 6)  # Rough USD
        }


# Global helper functions
def estimate_tokens(text: str) -> int:
    """Quick token estimation"""
    return TokenCounter.count_tokens(text)


def trim_history(history: List[Dict], max_tokens: int = 4000) -> List[Dict]:
    """Convenience function"""
    return TokenCounter.trim_to_token_limit(history, max_tokens)