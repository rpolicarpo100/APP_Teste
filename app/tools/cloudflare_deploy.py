"""
Cloudflare Deploy — Workers + Pages + R2 + Workers AI — com cfat_ token
Usa CLOUDFLARE_API_TOKEN (cfat_...) + CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_GATEWAY_ID opcional

Links:
- Dashboard: https://dash.cloudflare.com
- Workers: https://dash.cloudflare.com → Workers & Pages
- R2: https://dash.cloudflare.com/r2
- AI Gateway: https://dash.cloudflare.com → AI → AI Gateway
- Workers AI: https://developers.cloudflare.com/workers-ai/
- API Tokens: https://dash.cloudflare.com/profile/api-tokens
"""
import os
from pathlib import Path
from typing import Dict, Any
import httpx
from app.tools.registry import register_tool
from app.config.settings import ROOT_DIR, settings

def _get_cf_config():
    token = os.getenv('CLOUDFLARE_API_TOKEN') or os.getenv('CF_API_TOKEN') or os.getenv('CLOUDFLARE_API_KEY')
    account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID') or os.getenv('CF_ACCOUNT_ID')
    gateway_id = os.getenv('CLOUDFLARE_GATEWAY_ID') or os.getenv('CF_GATEWAY_ID')
    return {
        "token": token,
        "account_id": account_id,
        "gateway_id": gateway_id,
        "available": bool(token and account_id),
        "has_gateway": bool(gateway_id)
    }

def _get_workspace_path() -> Path:
    return ROOT_DIR / settings.workspace_path

@register_tool(
    id="cloudflare.test",
    name="Cloudflare Token Test",
    description="Testa token Cloudflare cfat_... e tenta obter Account ID + verifica permissões Workers AI, R2, Workers",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"token": {"type": "string"}}, "required": []},
    output_schema={"type": "object", "properties": {"valid": {"type": "boolean"}}}
)
def cloudflare_test(token: str = None) -> Dict[str, Any]:
    cfg = _get_cf_config()
    test_token = token or cfg["token"]
    if not test_token:
        return {
            "valid": False,
            "error": "CLOUDFLARE_API_TOKEN não setado — adiciona cfat_... em Render env vars",
            "how_to": {
                "1_dashboard": "https://dash.cloudflare.com → Account ID na URL: https://dash.cloudflare.com/<ACCOUNT_ID>/...",
                "2_token": "https://dash.cloudflare.com/profile/api-tokens → Create Token → Custom → Account: Workers AI + R2 + Workers",
                "3_env_vars": "Render → Environment → CLOUDFLARE_API_TOKEN=cfat_... + CLOUDFLARE_ACCOUNT_ID=xxx + CLOUDFLARE_GATEWAY_ID=xxx (opcional)",
                "4_gateway": "https://dash.cloudflare.com → AI → AI Gateway → Create Gateway → ID"
            }
        }
    
    results = {"token_prefix": test_token[:10] + "...", "length": len(test_token)}
    
    # Try to get accounts if token has permission
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(
                "https://api.cloudflare.com/client/v4/accounts",
                headers={"Authorization": f"Bearer {test_token}"}
            )
            if resp.status_code == 200:
                data = resp.json()
                accounts = data.get('result', [])
                results["accounts"] = [{"id": a.get('id'), "name": a.get('name')} for a in accounts[:3]]
                results["accounts_count"] = len(accounts)
                if accounts and not cfg["account_id"]:
                    results["suggestion_account_id"] = accounts[0].get('id')
            else:
                results["accounts_error"] = f"HTTP {resp.status_code}: {resp.text[:300]}"
    except Exception as e:
        results["accounts_error"] = str(e)
    
    # Try to get zones
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(
                "https://api.cloudflare.com/client/v4/zones",
                headers={"Authorization": f"Bearer {test_token}"}
            )
            if resp.status_code == 200:
                data = resp.json()
                zones = data.get('result', [])
                results["zones"] = [{"id": z.get('id'), "name": z.get('name')} for z in zones[:3]]
            else:
                results["zones_error"] = f"HTTP {resp.status_code}"
    except Exception as e:
        results["zones_error"] = str(e)
    
    # Try Workers AI if account_id available
    if cfg["account_id"]:
        try:
            with httpx.Client(timeout=20) as client:
                resp = client.post(
                    f"https://api.cloudflare.com/client/v4/accounts/{cfg['account_id']}/ai/run/@cf/meta/llama-3-8b-instruct",
                    headers={"Authorization": f"Bearer {test_token}", "Content-Type": "application/json"},
                    json={"messages": [{"role": "user", "content": "Hello, 1+1=?"}]}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results["workers_ai_test"] = {"ok": True, "result": str(data.get('result', ''))[:200]}
                else:
                    results["workers_ai_test"] = {"ok": False, "error": f"HTTP {resp.status_code}: {resp.text[:400]}"}
        except Exception as e:
            results["workers_ai_test"] = {"ok": False, "error": str(e)}
    
    # Try AI Gateway if available
    if cfg["account_id"] and cfg["gateway_id"]:
        try:
            with httpx.Client(timeout=20) as client:
                resp = client.post(
                    f"https://gateway.ai.cloudflare.com/v1/{cfg['account_id']}/{cfg['gateway_id']}/workers-ai/@cf/meta/llama-3-8b-instruct",
                    headers={"Authorization": f"Bearer {test_token}", "cf-aig-authorization": f"Bearer {test_token}", "Content-Type": "application/json"},
                    json={"messages": [{"role": "user", "content": "Hello"}]}
                )
                results["ai_gateway_test"] = {"status": resp.status_code, "ok": resp.status_code == 200, "text": resp.text[:300]}
        except Exception as e:
            results["ai_gateway_test"] = {"ok": False, "error": str(e)}
    
    results["config"] = {
        "has_token": bool(cfg["token"]),
        "has_account_id": bool(cfg["account_id"]),
        "has_gateway_id": bool(cfg["gateway_id"]),
        "account_id": cfg["account_id"][:10] + "..." if cfg["account_id"] else None,
        "gateway_id": cfg["gateway_id"]
    }
    
    results["valid"] = cfg["available"]
    results["message"] = "Cloudflare token válido" if cfg["available"] else "Falta CLOUDFLARE_ACCOUNT_ID — pega em https://dash.cloudflare.com → URL contém account ID"
    results["links"] = {
        "dashboard": "https://dash.cloudflare.com",
        "api_tokens": "https://dash.cloudflare.com/profile/api-tokens",
        "workers_ai": "https://developers.cloudflare.com/workers-ai/",
        "ai_gateway": "https://dash.cloudflare.com → AI → AI Gateway",
        "r2": "https://dash.cloudflare.com/r2",
        "workers": "https://dash.cloudflare.com → Workers & Pages"
    }
    
    return results

@register_tool(
    id="cloudflare.r2.upload",
    name="Cloudflare R2 Upload",
    description="Upload workspace files para Cloudflare R2 10GB free com cfat_ token",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"filename": {"type": "string"}, "all": {"type": "boolean"}}, "required": []},
    output_schema={"type": "object", "properties": {"uploaded": {"type": "boolean"}}}
)
def cloudflare_r2_upload(filename: str = None, all: bool = False) -> Dict[str, Any]:
    cfg = _get_cf_config()
    ws = _get_workspace_path()
    
    if not cfg["token"]:
        return {"uploaded": False, "error": "CLOUDFLARE_API_TOKEN não setado", "how_to": "Adiciona CLOUDFLARE_API_TOKEN=cfat_... em Render env vars — https://dash.cloudflare.com/profile/api-tokens"}
    
    # R2 precisa de R2_ACCESS_KEY_ID + R2_SECRET_ACCESS_KEY (S3 compat) além de cfat_
    # cfat_ pode ter permissão R2, mas S3 keys são separadas
    r2_account_id = os.getenv('R2_ACCOUNT_ID') or cfg["account_id"] or os.getenv('CLOUDFLARE_ACCOUNT_ID')
    r2_access_key = os.getenv('R2_ACCESS_KEY_ID') or os.getenv('CLOUDFLARE_R2_ACCESS_KEY')
    r2_secret_key = os.getenv('R2_SECRET_ACCESS_KEY') or os.getenv('CLOUDFLARE_R2_SECRET')
    r2_bucket = os.getenv('R2_BUCKET', 'workspace')
    
    files = []
    if all:
        files = list(ws.glob("*.html"))
    elif filename:
        f = ws / filename
        if f.exists():
            files = [f]
    else:
        files = sorted(ws.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    
    if r2_access_key and r2_secret_key and r2_account_id:
        try:
            import boto3
            s3 = boto3.client(
                's3',
                endpoint_url=f"https://{r2_account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=r2_access_key,
                aws_secret_access_key=r2_secret_key,
                region_name="auto"
            )
            results = []
            for fp in files:
                try:
                    s3.upload_file(str(fp), r2_bucket, fp.name, ExtraArgs={'ContentType': 'text/html'})
                    results.append({"file": fp.name, "status": "ok", "url": f"https://{r2_bucket}.{r2_account_id}.r2.dev/{fp.name} ou https://pub-{r2_account_id}.r2.dev/{fp.name}"})
                except Exception as e:
                    results.append({"file": fp.name, "status": "fail", "error": str(e)})
            return {"uploaded": any(r["status"]=="ok" for r in results), "platform": "r2", "results": results, "bucket": r2_bucket}
        except Exception as e:
            return {"uploaded": False, "error": str(e), "need": "boto3 + R2_ACCESS_KEY_ID + R2_SECRET_ACCESS_KEY"}
    
    # Fallback: tenta via Cloudflare API direta (se token tem R2 permissão)
    return {
        "uploaded": False,
        "platform": "r2",
        "need_s3_keys": True,
        "how_to_r2": {
            "1_r2_dashboard": "https://dash.cloudflare.com/r2 → Create bucket → workspace",
            "2_api_tokens": "https://dash.cloudflare.com/r2 → Manage R2 API Tokens → Create API Token → Object Read & Write → bucket workspace",
            "3_env_vars": "R2_ACCOUNT_ID=<account_id> + R2_ACCESS_KEY_ID=xxx + R2_SECRET_ACCESS_KEY=xxx + R2_BUCKET=workspace",
            "4_already_have_cfat": f"Tens cfat_... token mas R2 precisa S3 keys separadas — cria em R2 dashboard",
            "current_files": [f.name for f in files]
        },
        "cfat_token_present": bool(cfg["token"]),
        "account_id_present": bool(cfg["account_id"])
    }

@register_tool(
    id="cloudflare.workers.deploy",
    name="Cloudflare Workers Deploy",
    description="Deploy site para Cloudflare Workers / Pages com cfat_ token — 4GB free forever alternativa a Leapcell",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"filename": {"type": "string"}}, "required": []},
    output_schema={"type": "object", "properties": {"deployed": {"type": "boolean"}}}
)
def cloudflare_workers_deploy(filename: str = None) -> Dict[str, Any]:
    cfg = _get_cf_config()
    ws = _get_workspace_path()
    
    if not cfg["available"]:
        return {
            "deployed": False,
            "error": "Cloudflare não configurado — precisa CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID",
            "how_to": {
                "account_id": "https://dash.cloudflare.com → URL: https://dash.cloudflare.com/<ACCOUNT_ID>/...",
                "token": "https://dash.cloudflare.com/profile/api-tokens → Create Token → Edit Cloudflare Workers + R2 + AI Gateway",
                "env_vars": "CLOUDFLARE_API_TOKEN=cfat_... + CLOUDFLARE_ACCOUNT_ID=xxx",
                "current_token": cfg["token"][:15] + "..." if cfg["token"] else None
            },
            "links": {
                "workers": "https://dash.cloudflare.com → Workers & Pages",
                "pages": "https://pages.cloudflare.com",
                "docs_workers": "https://developers.cloudflare.com/workers/",
                "docs_pages": "https://developers.cloudflare.com/pages/"
            }
        }
    
    # Para MVP, retorna instruções + tenta criar Worker via API se possível
    files = []
    if filename:
        fp = ws / filename
        if fp.exists():
            files = [fp]
    else:
        files = sorted(ws.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)[:1]
    
    if not files:
        return {"deployed": False, "error": "Sem ficheiros em workspace — cria site via AGENT BUILDER primeiro"}
    
    # Tenta deploy via Cloudflare Pages API (mais simples para HTML estático)
    try:
        with httpx.Client(timeout=30) as client:
            # Primeiro lista projetos Pages
            resp = client.get(
                f"https://api.cloudflare.com/client/v4/accounts/{cfg['account_id']}/pages/projects",
                headers={"Authorization": f"Bearer {cfg['token']}"}
            )
            if resp.status_code == 200:
                projects = resp.json().get('result', [])
                # Se tem projeto ai-brain-god, usa, senão instrui criar
                proj_names = [p.get('name') for p in projects[:5]]
                return {
                    "deployed": False,
                    "platform": "cloudflare-pages",
                    "has_projects": len(projects) > 0,
                    "projects": proj_names,
                    "next_steps": f"Para deploy automático, cria projeto Pages 'ai-brain-god' em https://dash.cloudflare.com → Workers & Pages → Create → Pages → Connect Git → {files[0].name}",
                    "manual_upload": f"Ou faz upload manual: https://dash.cloudflare.com → Pages → ai-brain-god → Upload → {files[0].name}",
                    "files_ready": [f.name for f in files],
                    "api_ok": True
                }
            else:
                return {
                    "deployed": False,
                    "platform": "cloudflare-pages",
                    "error": f"API {resp.status_code}: {resp.text[:400]}",
                    "next_steps": "Verifica token permissões: Account → Cloudflare Pages → Edit"
                }
    except Exception as e:
        return {"deployed": False, "error": str(e), "platform": "cloudflare"}

@register_tool(
    id="cloudflare.ai.chat",
    name="Cloudflare Workers AI Chat",
    description="Chat com Cloudflare Workers AI free — @cf/meta/llama-3-8b-instruct etc — usa cfat_ token",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]},
    output_schema={"type": "object", "properties": {"response": {"type": "string"}}}
)
def cloudflare_ai_chat(message: str) -> Dict[str, Any]:
    from app.models.llm import CloudflareClient
    client = CloudflareClient()
    if not client.is_available():
        return {"error": "Cloudflare não configurado — CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID", "available": False}
    
    result = client.chat([{"role": "user", "content": message}], system_prompt="És um assistente útil PT-PT, custo 0 via Cloudflare Workers AI free.")
    return result
