"""
LLM Universal — tenta Ollama local, depois Groq free, Gemini free, OpenRouter free, Cloudflare Workers AI free, fallback local
Custo 0: Groq 14.4k req/dia sem cartão, Gemini 60 req/min sem cartão, OpenRouter free, Cloudflare Workers AI free
"""
import os
import httpx
from typing import List, Dict, Any, Optional
from app.config.settings import settings
from app.models.ollama import ollama_client

class GroqClient:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.model = os.getenv('GROQ_MODEL', 'groq/compound-mini')
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
        self.model = os.getenv('GEMINI_MODEL', 'gemini-flash-latest')
        self.base = "https://generativelanguage.googleapis.com/v1beta"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Dict[str, str]], system_prompt: str = None) -> Dict[str, Any]:
        if not self.is_available():
            return {"available": False, "error": "GEMINI_API_KEY não setado"}
        
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
    def __init__(self):
        self.api_key = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_API_KEY') or os.getenv('HF_API_KEY')
        self.model = os.getenv('HF_MODEL', 'meta-llama/Llama-3.1-8B-Instruct')
        self.base = "https://api-inference.huggingface.co/models"
        self.router_base = "https://router.huggingface.co/hf-inference/models"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Dict[str, str]], system_prompt: str = None) -> Dict[str, Any]:
        if not self.is_available():
            return {"available": False, "error": "HF_TOKEN não setado"}

        chat_messages = []
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})
        chat_messages.extend(messages)

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
                    last_error = f"HF {model_id} HTTP {resp.status_code}: {resp.text[:400]}"
                    if "depleted" in resp.text or "credits" in resp.text:
                        return {"available": False, "error": last_error, "needs_pro": True}
            except Exception as e:
                last_error = str(e)
                continue

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


class CloudflareClient:
    """
    Cloudflare Workers AI — free tier com CLOUDFLARE_API_TOKEN (cfat_...)
    Custo 0 sem cartão, usa Workers AI + AI Gateway
    Modelos free: @cf/meta/llama-3-8b-instruct, @cf/mistral/mistral-7b-instruct-v0.1, @cf/google/gemma-3-12b-it, etc
    Docs: https://developers.cloudflare.com/workers-ai/ + https://developers.cloudflare.com/ai-gateway/
    Token format: cfat_... (Account API Token) ou cfut_... (User API Token)
    Precisa: CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID (+ CLOUDFLARE_GATEWAY_ID opcional para AI Gateway)
    """
    def __init__(self):
        self.api_key = os.getenv('CLOUDFLARE_API_TOKEN') or os.getenv('CF_API_TOKEN') or os.getenv('CLOUDFLARE_API_KEY')
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID') or os.getenv('CF_ACCOUNT_ID')
        self.gateway_id = os.getenv('CLOUDFLARE_GATEWAY_ID') or os.getenv('CF_GATEWAY_ID')
        self.model = os.getenv('CLOUDFLARE_MODEL', '@cf/meta/llama-3.3-70b-instruct-fp8-fast')  # 2026-05-30 llama-3-8b deprecated, cfut_ token tested OK
        # Modelos que funcionam free — testado 2026-09-14 com cfut_... (validado 2026-09-14)
        # @cf/meta/llama-3-8b-instruct deprecated 2026-05-30 → 410, @cf/google/gemma-3-12b-it → 403 not allowed
        # Funcionam: llama-3.3-70b-fp8-fast (200) + gpt-oss-120b (200) com account 2994d6fc...
        self.models_to_try = [
            self.model,
            '@cf/meta/llama-3.3-70b-instruct-fp8-fast',
            '@cf/openai/gpt-oss-120b',
            '@cf/meta/llama-3-8b-instruct',  # deprecated 2026-05-30 mas mantém fallback
            '@cf/mistral/mistral-7b-instruct-v0.1',
            '@cf/qwen/qwen2.5-coder-32b-instruct',
            '@cf/deepseek-ai/deepseek-r1-distill-qwen-32b',
            '@cf/google/gemma-3-12b-it'  # 403 not allowed neste account
        ]

    def is_available(self) -> bool:
        return bool(self.api_key and self.account_id)

    def chat(self, messages: List[Dict[str, str]], system_prompt: str = None) -> Dict[str, Any]:
        if not self.is_available():
            missing = []
            if not self.api_key:
                missing.append("CLOUDFLARE_API_TOKEN (cfat_...)")
            if not self.account_id:
                missing.append("CLOUDFLARE_ACCOUNT_ID")
            return {"available": False, "error": f"Cloudflare não configurado — falta: {', '.join(missing)} — https://dash.cloudflare.com → Account ID + AI Gateway"}

        # Converte messages para formato Cloudflare
        # Cloudflare Workers AI espera: {"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]}
        cf_messages = []
        if system_prompt:
            cf_messages.append({"role": "system", "content": system_prompt})
        cf_messages.extend(messages)

        # Tenta primeiro via AI Gateway se gateway_id disponível (recomendado, tem cache + analytics)
        # Docs: https://developers.cloudflare.com/ai-gateway/usage/rest-api/
        # Endpoint: https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/workers-ai/{model}
        # Ou compat: https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/compat (OpenAI compat)
        
        last_error = None
        
        # Método 1: AI Gateway compat (OpenAI compat) — mais fiável
        if self.gateway_id:
            for model_id in self.models_to_try:
                try:
                    # OpenAI compat via AI Gateway
                    # model format: workers-ai/@cf/meta/llama-3-8b-instruct
                    compat_model = f"workers-ai/{model_id}" if not model_id.startswith("workers-ai/") else model_id
                    with httpx.Client(timeout=45) as client:
                        resp = client.post(
                            f"https://gateway.ai.cloudflare.com/v1/{self.account_id}/{self.gateway_id}/compat/chat/completions",
                            headers={
                                "Authorization": f"Bearer {self.api_key}",
                                "Content-Type": "application/json",
                                "cf-aig-authorization": f"Bearer {self.api_key}"
                            },
                            json={
                                "model": compat_model,
                                "messages": cf_messages,
                                "max_tokens": 1024,
                                "temperature": 0.7
                            }
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            # OpenAI format
                            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                            if content:
                                return {"content": content, "model": model_id, "available": True, "provider": "cloudflare", "raw": data, "via": "ai-gateway-compat"}
                        last_error = f"CF Gateway compat {model_id} HTTP {resp.status_code}: {resp.text[:500]}"
                except Exception as e:
                    last_error = str(e)
                    continue

            # Método 1b: AI Gateway workers-ai direct
            for model_id in self.models_to_try:
                try:
                    with httpx.Client(timeout=45) as client:
                        resp = client.post(
                            f"https://gateway.ai.cloudflare.com/v1/{self.account_id}/{self.gateway_id}/workers-ai/{model_id}",
                            headers={
                                "Authorization": f"Bearer {self.api_key}",
                                "Content-Type": "application/json",
                                "cf-aig-authorization": f"Bearer {self.api_key}"
                            },
                            json={
                                "messages": cf_messages,
                                "max_tokens": 1024
                            }
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            # Workers AI format pode ser {"result": {"response": "..."}} ou direct
                            if isinstance(data, dict):
                                if 'result' in data:
                                    result = data['result']
                                    if isinstance(result, dict):
                                        content = result.get('response') or result.get('content') or str(result)
                                    else:
                                        content = str(result)
                                else:
                                    content = data.get('response') or data.get('content') or str(data)
                                if content and len(content) > 5:
                                    return {"content": content, "model": model_id, "available": True, "provider": "cloudflare", "raw": data, "via": "ai-gateway-direct"}
                        last_error = f"CF Gateway direct {model_id} HTTP {resp.status_code}: {resp.text[:500]}"
                except Exception as e:
                    last_error = str(e)
                    continue

        # Método 2: Direct Workers AI API (sem gateway) — https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}
        for model_id in self.models_to_try:
            try:
                with httpx.Client(timeout=45) as client:
                    resp = client.post(
                        f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{model_id}",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "messages": cf_messages,
                            "max_tokens": 1024
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get('success'):
                            result = data.get('result', {})
                            if isinstance(result, dict):
                                content = result.get('response') or result.get('content') or str(result)
                            else:
                                content = str(result)
                            if content and len(content) > 5:
                                return {"content": content, "model": model_id, "available": True, "provider": "cloudflare", "raw": data, "via": "direct-api"}
                        else:
                            # Pode ser formato diferente
                            content = str(data.get('result', '')) or str(data)
                            if len(content) > 10:
                                return {"content": content, "model": model_id, "available": True, "provider": "cloudflare", "raw": data, "via": "direct-api-fallback"}
                    last_error = f"CF Direct {model_id} HTTP {resp.status_code}: {resp.text[:500]}"
            except Exception as e:
                last_error = str(e)
                continue

        return {"available": False, "error": last_error or "Cloudflare Workers AI falhou — verifica CLOUDFLARE_ACCOUNT_ID + token permissões Workers AI"}


class UniversalLLM:
    def __init__(self):
        self.ollama = ollama_client
        self.groq = GroqClient()
        self.gemini = GeminiClient()
        self.openrouter = OpenRouterClient()
        self.huggingface = HuggingFaceClient()
        self.cloudflare = CloudflareClient()

    def is_any_available(self) -> bool:
        return self.ollama.is_available() or self.groq.is_available() or self.gemini.is_available() or self.openrouter.is_available() or self.huggingface.is_available() or self.cloudflare.is_available()

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
        if self.cloudflare.is_available():
            providers.append("cloudflare")
        return providers

    def chat(self, messages: List[Dict[str, str]], system_prompt: str = None) -> Dict[str, Any]:
        # Try in order: Ollama local -> Groq free -> Gemini free -> Cloudflare free -> OpenRouter free -> HuggingFace -> fallback

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

        # 4. Cloudflare Workers AI free (NOVO — com token cfat_...)
        if self.cloudflare.is_available():
            result = self.cloudflare.chat(messages, system_prompt)
            if result.get('available') and result.get('content'):
                return result

        # 5. OpenRouter free
        if self.openrouter.is_available():
            result = self.openrouter.chat(messages, system_prompt)
            if result.get('available') and result.get('content'):
                return result

        # 6. HuggingFace Inference free
        if self.huggingface.is_available():
            result = self.huggingface.chat(messages, system_prompt)
            if result.get('available') and result.get('content'):
                return result

        # Fallback local without LLM
        return {
            "content": "LLM não disponível — modo fallback local. Configure GROQ_API_KEY (free 14.4k/dia sem cartão em console.groq.com) ou GEMINI_API_KEY (free 60/min) ou CLOUDFLARE_API_TOKEN (cfat_... free em dash.cloudflare.com) + CLOUDFLARE_ACCOUNT_ID ou OPENROUTER_API_KEY ou HF_TOKEN para ativar LLM em produção custo 0.",
            "model": "fallback",
            "available": False,
            "provider": "fallback",
            "error": "CAPACIDADE NÃO DISPONÍVEL — nenhum LLM configurado",
            "suggestion": "Custo 0: Groq free em https://console.groq.com → GROQ_API_KEY, Gemini free em https://aistudio.google.com → GEMINI_API_KEY, Cloudflare Workers AI free em https://dash.cloudflare.com → CLOUDFLARE_API_TOKEN (cfat_...) + CLOUDFLARE_ACCOUNT_ID, HuggingFace free em https://huggingface.co/settings/tokens → HF_TOKEN"
        }

llm_client = UniversalLLM()
