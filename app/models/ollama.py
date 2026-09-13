"""
Ollama client — Local AI Brain §5
LLM não controla directamente o computador. LLM pede acções ao Brain.
"""
import httpx
from typing import List, Dict, Any, Optional
from app.config.settings import settings
import json

class OllamaClient:
    def __init__(self, host: str = None, model: str = None, timeout: int = None):
        self.host = host or settings.ollama_host
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.ollama_timeout

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=5) as client:
                resp = client.get(f"{self.host}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(f"{self.host}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def chat(self, messages: List[Dict[str, str]], system_prompt: str = None) -> Dict[str, Any]:
        """
        Chat com Ollama — retorna resposta.
        Se Ollama não disponível, retorna limitação sem inventar.
        """
        if not self.is_available():
            return {
                "content": "Ollama não disponível neste ambiente. Modo fallback: usar lógica local sem LLM.",
                "model": self.model,
                "available": False,
                "error": "CAPACIDADE NÃO DISPONÍVEL — Ollama não acessível"
            }

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        if system_prompt:
            payload["messages"] = [{"role": "system", "content": system_prompt}] + messages

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.host}/api/chat", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "content": data.get("message", {}).get("content", ""),
                        "model": self.model,
                        "available": True,
                        "raw": data
                    }
                else:
                    return {"error": f"HTTP {resp.status_code}", "content": "", "available": False}
        except Exception as e:
            return {"error": str(e), "content": "", "available": False}

    def generate(self, prompt: str, system: str = None) -> Dict[str, Any]:
        if not self.is_available():
            return {"content": "", "available": False, "error": "Ollama não disponível"}
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.host}/api/generate", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return {"content": data.get("response", ""), "available": True, "raw": data}
                else:
                    return {"error": f"HTTP {resp.status_code}", "available": False}
        except Exception as e:
            return {"error": str(e), "available": False}

# Singleton
ollama_client = OllamaClient()
