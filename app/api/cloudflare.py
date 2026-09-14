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
    account_id: Optional[str] = None
    gateway_id: Optional[str] = None

class CloudflareUploadRequest(BaseModel):
    filename: Optional[str] = None
    all: bool = False

class CloudflareR2SetupRequest(BaseModel):
    account_id: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    bucket: Optional[str] = None

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
    return cloudflare_test(token=req.token, account_id=req.account_id, gateway_id=req.gateway_id)

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

@router.post("/cloudflare/r2/setup")
def r2_setup(req: CloudflareR2SetupRequest):
    """Setup R2 bucket com keys via body — cria bucket ai-brain-workspace e testa upload — para usar quando env vars ainda não setadas em Render"""
    import os
    from pathlib import Path
    # Usa keys do body ou fallback env vars
    account_id = req.account_id or os.getenv('R2_ACCOUNT_ID') or os.getenv('CLOUDFLARE_ACCOUNT_ID')
    access_key = req.access_key_id or os.getenv('R2_ACCESS_KEY_ID')
    secret_key = req.secret_access_key or os.getenv('R2_SECRET_ACCESS_KEY')
    bucket = req.bucket or os.getenv('R2_BUCKET', 'ai-brain-workspace')
    
    if not account_id or not access_key or not secret_key:
        return {"ok": False, "error": "Falta account_id + access_key_id + secret_access_key — envia via body ou seta env vars R2_ACCOUNT_ID + R2_ACCESS_KEY_ID + R2_SECRET_ACCESS_KEY"}
    
    try:
        import boto3
        from botocore.config import Config
        import ssl
        import sys
        # Try to get OpenSSL version for debugging
        openssl_version = ssl.OPENSSL_VERSION
        python_version = sys.version
        
        # Try with virtual addressing and TLS fix
        s3 = boto3.client(
            's3',
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='auto',
            config=Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path'},
                connect_timeout=15,
                read_timeout=15
            )
        )
        # Try list buckets
        buckets = []
        try:
            resp = s3.list_buckets()
            buckets = [b['Name'] for b in resp.get('Buckets', [])]
        except Exception as e:
            buckets = [f"list error: {e}"]
        
        # Try create bucket
        create_result = None
        try:
            s3.create_bucket(Bucket=bucket)
            create_result = f"Bucket {bucket} criado OK"
        except Exception as e:
            err = str(e)
            if "BucketAlreadyOwnedByYou" in err or "BucketAlreadyExists" in err or "already" in err.lower():
                create_result = f"Bucket {bucket} já existe — OK"
            else:
                create_result = f"Create bucket error: {err[:500]}"
        
        # Try upload test file
        upload_result = None
        try:
            from app.config.settings import ROOT_DIR, settings
            ws = ROOT_DIR / settings.workspace_path
            ws.mkdir(parents=True, exist_ok=True)
            test_file = ws / "r2_test.html"
            test_file.write_text(f"<h1>R2 OK {bucket}</h1><p>Test {account_id}</p>", encoding='utf-8')
            s3.upload_file(str(test_file), bucket, "r2_test.html", ExtraArgs={'ContentType': 'text/html'})
            upload_result = f"Upload r2_test.html OK para {bucket}"
        except Exception as e:
            upload_result = f"Upload error: {e}"
        
        return {
            "ok": True,
            "account_id": account_id[:10] + "...",
            "bucket": bucket,
            "buckets_existing": buckets,
            "create_result": create_result,
            "upload_result": upload_result,
            "endpoint": f"https://{account_id}.r2.cloudflarestorage.com",
            "public_url": f"https://{bucket}.{account_id}.r2.dev/r2_test.html ou https://pub-{account_id}.r2.dev/r2_test.html",
            "openssl_version": openssl_version,
            "python_version": python_version,
            "message": f"R2 {bucket} setup — se OK, adiciona env vars em Render: R2_ACCOUNT_ID={account_id} R2_ACCESS_KEY_ID=xxx R2_SECRET_ACCESS_KEY=xxx R2_BUCKET={bucket} — Se SSL fail, cria bucket manualmente em https://dash.cloudflare.com/r2"
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "account_id": account_id[:10] + "..." if account_id else None}

@router.get("/cloudflare/r2/tls-test")
def r2_tls_test():
    """Testa TLS handshake para R2 endpoint — debug SSLV3_ALERT_HANDSHAKE_FAILURE"""
    import ssl
    import sys
    import httpx
    results = {
        "openssl_version": ssl.OPENSSL_VERSION,
        "python_version": sys.version,
        "tests": []
    }
    endpoints = [
        "https://2994d6fc57ed22ae8ad47c3525cc3dae.r2.cloudflarestorage.com/",
        "https://r2.cloudflarestorage.com/",
        "https://cloudflare.com/",
        "https://api.cloudflare.com/",
        "https://www.google.com/"
    ]
    for ep in endpoints:
        try:
            with httpx.Client(timeout=10, verify=True) as c:
                r = c.get(ep)
                results["tests"].append({"endpoint": ep, "status": r.status_code, "ok": True, "headers": dict(list(r.headers.items())[:3])})
        except Exception as e:
            results["tests"].append({"endpoint": ep, "ok": False, "error": str(e)[:500]})
    
    # Also test with verify=False
    try:
        with httpx.Client(timeout=10, verify=False) as c:
            r = c.get("https://2994d6fc57ed22ae8ad47c3525cc3dae.r2.cloudflarestorage.com/", headers={"Host": "2994d6fc57ed22ae8ad47c3525cc3dae.r2.cloudflarestorage.com"})
            results["tests"].append({"endpoint": "R2 with verify=False", "status": r.status_code, "ok": True})
    except Exception as e:
        results["tests"].append({"endpoint": "R2 with verify=False", "ok": False, "error": str(e)[:500]})
    
    return results


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
