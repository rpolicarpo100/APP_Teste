"""
LLM Universal — tenta Ollama local, depois Groq free, Gemini free, OpenRouter free, fallback local
Custo 0: Groq 14.4k req/dia sem cartão, Gemini 60 req/min sem cartão, OpenRouter free
"""
import os
import httpx
from typing import List, Dict, Any, Optional
from app.config.settings import settings
from app.models.ollama import ollama_client

class GroqClient:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.model = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')  # free tier model
        self.base = "https://api.groq.com/openai/v1"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Dict[str, str]], system_prompt: str = None) -> Dict[str, Any]:
        if not self.is_available():
            return {"available": False, "error": "GROQ_API_KEY não setado"}
        
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        msgs.extend(messages)

        payload = {
            "model": self.model,
            "messages": msgs,
            "temperature": 0.7,
            "max_tokens": 1024
        }

        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    f"{self.base}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=payload
                )
                if resp.status_code == 200:
                    data = resp.json()
                    content = data['choices'][0]['message']['content']
                    return {"content": content, "model": self.model, "available": True, "provider": "groq", "raw": data}
                else:
                    return {"available": False, "error": f"Groq HTTP {resp.status_code}: {resp.text[:200]}"}
        except Exception as e:
            return {"available": False, "error": str(e)}

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        self.model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')  # free tier
        self.base = "https://generativelanguage.googleapis.com/v1beta"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Dict[str, str]], system_prompt: str = None) -> Dict[str, Any]:
        if not self.is_available():
            return {"available": False, "error": "GEMINI_API_KEY não setado"}
        
        # Convert messages to Gemini format
        # Gemini uses contents with parts
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System: {system_prompt}"}]})
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

        payload = {"contents": contents}

        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    f"{self.base}/models/{self.model}:generateContent?key={self.api_key}",
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
                if resp.status_code == 200:
                    data = resp.json()
                    # Extract text
                    candidates = data.get('candidates', [])
                    if candidates:
                        parts = candidates[0].get('content', {}).get('parts', [])
                        content = "".join([p.get('text','') for p in parts])
                        return {"content": content, "model": self.model, "available": True, "provider": "gemini", "raw": data}
                    return {"available": False, "error": "No candidates"}
                else:
                    return {"available": False, "error": f"Gemini HTTP {resp.status_code}: {resp.text[:200]}"}
        except Exception as e:
            return {"available": False, "error": str(e)}

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.model = os.getenv('OPENROUTER_MODEL', 'meta-llama/llama-3.1-8b-instruct:free')
        self.base = "https://openrouter.ai/api/v1"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Dict[str, str]], system_prompt: str = None) -> Dict[str, Any]:
        if not self.is_available():
            return {"available": False, "error": "OPENROUTER_API_KEY não setado"}
        
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        msgs.extend(messages)

        payload = {
            "model": self.model,
            "messages": msgs
        }

        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    f"{self.base}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "HTTP-Referer": "https://app-teste-x6od.onrender.com", "X-Title": "AI Brain GOD"},
                    json=payload
                )
                if resp.status_code == 200:
                    data = resp.json()
                    content = data['choices'][0]['message']['content']
                    return {"content": content, "model": self.model, "available": True, "provider": "openrouter", "raw": data}
                else:
                    return {"available": False, "error": f"OpenRouter HTTP {resp.status_code}: {resp.text[:200]}"}
        except Exception as e:
            return {"available": False, "error": str(e)}

class UniversalLLM:
    def __init__(self):
        self.ollama = ollama_client
        self.groq = GroqClient()
        self.gemini = GeminiClient()
        self.openrouter = OpenRouterClient()

    def is_any_available(self) -> bool:
        return self.ollama.is_available() or self.groq.is_available() or self.gemini.is_available() or self.openrouter.is_available()

    def get_available_providers(self) -> List[str]:
        providers = []
        if self.ollama.is_available():
            providers.append("ollama")
        if self.groq.is_available():
            providers.append("groq")
        if self.gemini.is_available():
            providers.append("gemini")
        if self.openrouter.is_available():
            providers.append("openrouter")
        return providers

    def chat(self, messages: List[Dict[str, str]], system_prompt: str = None) -> Dict[str, Any]:
        # Try in order: Ollama local -> Groq free -> Gemini free -> OpenRouter free -> fallback
        # Each provider is checked via Tools Health ranking for best available

        # 1. Ollama local
        if self.ollama.is_available():
            result = self.ollama.chat(messages, system_prompt)
            if result.get('available') and result.get('content'):
                result['provider'] = 'ollama'
                return result

        # 2. Groq free (14.4k req/day, no card)
        if self.groq.is_available():
            result = self.groq.chat(messages, system_prompt)
            if result.get('available') and result.get('content'):
                return result

        # 3. Gemini free (60 req/min)
        if self.gemini.is_available():
            result = self.gemini.chat(messages, system_prompt)
            if result.get('available') and result.get('content'):
                return result

        # 4. OpenRouter free
        if self.openrouter.is_available():
            result = self.openrouter.chat(messages, system_prompt)
            if result.get('available') and result.get('content'):
                return result

        # Fallback local without LLM
        return {
            "content": "LLM não disponível — modo fallback local. Configure GROQ_API_KEY (free 14.4k/dia sem cartão em console.groq.com) ou GEMINI_API_KEY (free 60/min) ou OPENROUTER_API_KEY para ativar LLM em produção custo 0.",
            "model": "fallback",
            "available": False,
            "provider": "fallback",
            "error": "CAPACIDADE NÃO DISPONÍVEL — nenhum LLM configurado",
            "suggestion": "Custo 0: Groq free tier sem cartão em https://console.groq.com → GROQ_API_KEY, ou Gemini free em https://aistudio.google.com → GEMINI_API_KEY"
        }

llm_client = UniversalLLM()
