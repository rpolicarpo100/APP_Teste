"""
Cloudflare API — Workers AI + R2 + Workers Deploy
Endpoints para usar token cfat_... recebido
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.tools.cloudflare_deploy import cloudflare_test, cloudflare_r2_upload, cloudflare_workers_deploy, cloudflare_ai_chat

router = APIRouter()

class CloudflareTestRequest(BaseModel):
    token: Optional[str] = None

class CloudflareUploadRequest(BaseModel):
    filename: Optional[str] = None
    all: bool = False

class CloudflareDeployRequest(BaseModel):
    filename: Optional[str] = None

class CloudflareChatRequest(BaseModel):
    message: str

@router.get("/cloudflare/test")
def test_cloudflare():
    """Testa token Cloudflare cfat_... e verifica permissões"""
    return cloudflare_test()

@router.post("/cloudflare/test")
def test_cloudflare_post(req: CloudflareTestRequest):
    return cloudflare_test(token=req.token)

@router.get("/cloudflare/r2/status")
def r2_status():
    from app.tools.persistent_storage import workspace_persist_status
    return workspace_persist_status()

@router.post("/cloudflare/r2/upload")
def r2_upload(req: CloudflareUploadRequest):
    return cloudflare_r2_upload(filename=req.filename, all=req.all)

@router.get("/cloudflare/r2/upload")
def r2_upload_get(filename: Optional[str] = None, all: bool = False):
    return cloudflare_r2_upload(filename=filename, all=all)

@router.post("/cloudflare/workers/deploy")
def workers_deploy(req: CloudflareDeployRequest):
    return cloudflare_workers_deploy(filename=req.filename)

@router.get("/cloudflare/workers/deploy")
def workers_deploy_get(filename: Optional[str] = None):
    return cloudflare_workers_deploy(filename=filename)

@router.post("/cloudflare/ai/chat")
def ai_chat(req: CloudflareChatRequest):
    return cloudflare_ai_chat(message=req.message)

@router.get("/cloudflare/ai/models")
def ai_models():
    return {
        "models": [
            "@cf/meta/llama-3-8b-instruct",
            "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
            "@cf/mistral/mistral-7b-instruct-v0.1",
            "@cf/google/gemma-3-12b-it",
            "@cf/qwen/qwen2.5-coder-32b-instruct",
            "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b",
            "@cf/openai/gpt-oss-120b"
        ],
        "free_tier": "10k requests/dia — https://developers.cloudflare.com/workers-ai/platform/pricing/",
        "docs": "https://developers.cloudflare.com/workers-ai/models/",
        "endpoints": {
            "direct": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}",
            "gateway": "https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/workers-ai/{model}",
            "compat": "https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/compat/chat/completions"
        },
        "how_to": "CLOUDFLARE_API_TOKEN=cfat_... + CLOUDFLARE_ACCOUNT_ID=xxx + CLOUDFLARE_GATEWAY_ID=ai-brain-god (opcional)"
    }
