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
        self.model = os.getenv('GROQ_MODEL', 'groq/compound-mini')  # free tier model
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
        self.model = os.getenv('GEMINI_MODEL', 'gemini-flash-latest')  # free tier
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
        self.model = os.getenv('OPENROUTER_MODEL', 'nvidia/nemotron-3.5-lightning:free')
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


class HuggingFaceClient:
    """
    Hugging Face Inference API — free tier com HF_TOKEN
    Custo 0 sem cartão, usa Inference Providers
    Modelos free: Qwen2.5-7B-Instruct, Llama-3.2-3B-Instruct, etc
    """
    def __init__(self):
        self.api_key = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_API_KEY') or os.getenv('HF_API_KEY')
        self.model = os.getenv('HF_MODEL', 'meta-llama/Llama-3.1-8B-Instruct')
        # Nova Inference API router
        self.base = "https://api-inference.huggingface.co/models"
        self.router_base = "https://router.huggingface.co/hf-inference/models"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Dict[str, str]], system_prompt: str = None) -> Dict[str, Any]:
        if not self.is_available():
            return {"available": False, "error": "HF_TOKEN não setado"}

        # Novo Inference Providers — chat completions (router.huggingface.co)
        # Docs: https://huggingface.co/docs/inference-providers/index
        # Free tier tem créditos mensais limitados, PRO tem 20x mais
        chat_messages = []
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})
        chat_messages.extend(messages)

        # Modelos que funcionam com Inference Providers free (se créditos disponíveis)
        models_to_try = [self.model, "meta-llama/Llama-3.1-8B-Instruct", "mistralai/Mistral-7B-Instruct-v0.3"]

        for model_id in models_to_try:
            try:
                with httpx.Client(timeout=30) as client:
                    resp = client.post(
                        "https://router.huggingface.co/v1/chat/completions",
                        headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                        json={
                            "model": model_id,
                            "messages": chat_messages,
                            "max_tokens": 512,
                            "temperature": 0.7
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                        if content:
                            return {"content": content, "model": model_id, "available": True, "provider": "huggingface", "raw": data}
                    # Guarda erro para debug
                    last_error = f"HF {model_id} HTTP {resp.status_code}: {resp.text[:400]}"
                    # Se créditos esgotados, não tenta outros
                    if "depleted" in resp.text or "credits" in resp.text:
                        return {"available": False, "error": last_error, "needs_pro": True}
            except Exception as e:
                last_error = str(e)
                continue

        # Fallback para legacy text generation (se DNS permitir)
        try:
            prompt_parts = []
            if system_prompt:
                prompt_parts.append(f"System: {system_prompt}")
            for m in messages:
                prompt_parts.append(f"{m['role']}: {m['content']}")
            prompt_parts.append("Assistant:")
            full_prompt = "\n".join(prompt_parts)

            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    f"{self.router_base}/{self.model}",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={
                        "inputs": full_prompt,
                        "parameters": {"max_new_tokens": 512, "temperature": 0.7, "return_full_text": False},
                        "options": {"wait_for_model": True}
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        content = data[0].get('generated_text', '') if isinstance(data[0], dict) else str(data[0])
                    elif isinstance(data, dict):
                        content = data.get('generated_text', '')
                    else:
                        content = str(data)
                    if content:
                        return {"content": content, "model": self.model, "available": True, "provider": "huggingface", "raw": data}
                last_error = f"HF legacy HTTP {resp.status_code}: {resp.text[:400]}"
        except Exception as e:
            last_error = str(e)

        return {"available": False, "error": last_error if 'last_error' in locals() else "HF inference failed"}


class UniversalLLM:
    def __init__(self):
        self.ollama = ollama_client
        self.groq = GroqClient()
        self.gemini = GeminiClient()
        self.openrouter = OpenRouterClient()
        self.huggingface = HuggingFaceClient()

    def is_any_available(self) -> bool:
        return self.ollama.is_available() or self.groq.is_available() or self.gemini.is_available() or self.openrouter.is_available() or self.huggingface.is_available()

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
        if self.huggingface.is_available():
            providers.append("huggingface")
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

        # 5. HuggingFace Inference free (HF_TOKEN sem cartão)
        if self.huggingface.is_available():
            result = self.huggingface.chat(messages, system_prompt)
            if result.get('available') and result.get('content'):
                return result

        # Fallback local without LLM
        return {
            "content": "LLM não disponível — modo fallback local. Configure GROQ_API_KEY (free 14.4k/dia sem cartão em console.groq.com) ou GEMINI_API_KEY (free 60/min) ou OPENROUTER_API_KEY ou HF_TOKEN (free HuggingFace Inference sem cartão em huggingface.co/settings/tokens) para ativar LLM em produção custo 0.",
            "model": "fallback",
            "available": False,
            "provider": "fallback",
            "error": "CAPACIDADE NÃO DISPONÍVEL — nenhum LLM configurado",
            "suggestion": "Custo 0: Groq free tier sem cartão em https://console.groq.com → GROQ_API_KEY, ou Gemini free em https://aistudio.google.com → GEMINI_API_KEY, ou HuggingFace free em https://huggingface.co/settings/tokens → HF_TOKEN"
        }

llm_client = UniversalLLM()
