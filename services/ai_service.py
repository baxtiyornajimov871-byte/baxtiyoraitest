"""
BaxtiyorAiTest - AI Service
Advanced AI orchestration with Groq, HuggingFace, and intelligent fallback
"""

import requests
import time
from typing import Dict, Any, List
from app.config import Config


class AIService:
    """Advanced AI Service with Multi-Provider Support & Fallback"""

    @staticmethod
    def call_groq(prompt: str, model: str = "llama3-70b-8192", 
                  temperature: float = 0.7, max_tokens: int = 2048, 
                  system_prompt: str = None) -> Dict:
        """Call Groq API (Fastest)"""
        if not Config.GROQ_API_KEY:
            return {"error": "Groq API key not configured"}

        headers = {
            "Authorization": f"Bearer {Config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        try:
            start_time = time.time()
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            latency = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                
                return {
                    "success": True,
                    "content": content,
                    "model": model,
                    "provider": "groq",
                    "latency_ms": latency,
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
            else:
                return {"error": f"Groq API Error: {response.text}", "provider": "groq"}

        except Exception as e:
            return {"error": str(e), "provider": "groq"}

    @staticmethod
    def call_huggingface(prompt: str, model: str = "mistralai/Mistral-7B-Instruct-v0.2",
                        temperature: float = 0.7, max_tokens: int = 2048):
        """Call HuggingFace Inference API"""
        if not Config.HUGGINGFACE_API_KEY:
            return {"error": "HuggingFace API key not configured"}

        headers = {
            "Authorization": f"Bearer {Config.HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_tokens,
                "return_full_text": False
            }
        }

        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                json=payload,
                headers=headers,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                content = data[0]["generated_text"] if isinstance(data, list) else data.get("generated_text", "")
                return {
                    "success": True,
                    "content": content,
                    "model": model,
                    "provider": "huggingface"
                }
            else:
                return {"error": f"HuggingFace Error: {response.text}", "provider": "huggingface"}

        except Exception as e:
            return {"error": str(e), "provider": "huggingface"}

    @staticmethod
    def fallback_response(prompt: str):
        """Internal fallback engine when all providers fail"""
        return {
            "success": True,
            "content": "I'm currently experiencing high load. Please try again in a moment. I'm here to help!",
            "model": "fallback-engine",
            "provider": "internal"
        }

    @staticmethod
    def generate_response(prompt: str, model: str = "llama3-70b-8192",
                         temperature: float = 0.7, system_prompt: str = None,
                         conversation_history: List = None):
        """Main method with smart provider routing and fallback"""
        
        # Prepare full context with history
        full_prompt = prompt
        if conversation_history:
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-10:]])
            full_prompt = f"{history_text}\n\nUser: {prompt}"

        # Try Groq first (fastest)
        result = AIService.call_groq(
            prompt=full_prompt,
            model=model,
            temperature=temperature,
            system_prompt=system_prompt
        )

        if "error" not in result:
            return result

        # Fallback to HuggingFace
        print("Groq failed, trying HuggingFace...")
        result = AIService.call_huggingface(
            prompt=full_prompt,
            temperature=temperature
        )

        if "error" not in result:
            return result

        # Final fallback
        print("All providers failed. Using internal fallback.")
        return AIService.fallback_response(prompt)

    @staticmethod
    def get_available_models():
        """Return available models with provider info"""
        return {
            "groq": [
                "llama3-70b-8192",
                "llama3-8b-8192",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ],
            "huggingface": [
                "mistralai/Mistral-7B-Instruct-v0.2",
                "google/gemma-7b-it"
            ]
        }