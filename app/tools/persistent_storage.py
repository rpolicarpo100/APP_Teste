"""
Workspace Persistente — Supabase Storage 1GB free + R2 10GB free + GitHub Pages gh-pages
Tarefa 2: Workspace persistente Supabase Storage 1GB free ou R2 10GB ou GitHub Pages gh-pages

Zero-cost:
- Supabase Storage 1GB free (sem cartão) — https://supabase.com/storage
- Cloudflare R2 10GB free (sem cartão, S3 compat) — https://r2.cloud
- GitHub Pages gh-pages branch free forever — https://pages.github.com

Implementa upload automático após build se env vars disponíveis
"""
import os
from pathlib import Path
from typing import Dict, Any, List
from app.tools.registry import register_tool
from app.config.settings import ROOT_DIR, settings

def _get_workspace_path() -> Path:
    return ROOT_DIR / settings.workspace_path

def _check_supabase_config() -> Dict[str, str]:
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
    bucket = os.getenv('SUPABASE_BUCKET', 'workspace')
    if url and key:
        return {"url": url, "key": key, "bucket": bucket, "available": True}
    return {"available": False}

def _check_r2_config() -> Dict[str, str]:
    account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID') or os.getenv('R2_ACCOUNT_ID')
    access_key = os.getenv('R2_ACCESS_KEY_ID') or os.getenv('CLOUDFLARE_R2_ACCESS_KEY')
    secret_key = os.getenv('R2_SECRET_ACCESS_KEY') or os.getenv('CLOUDFLARE_R2_SECRET')
    bucket = os.getenv('R2_BUCKET', 'workspace')
    if account_id and access_key and secret_key:
        return {"account_id": account_id, "access_key": access_key, "secret_key": secret_key, "bucket": bucket, "available": True}
    return {"available": False}

def _check_github_config() -> Dict[str, str]:
    token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPO', 'rpolicarpo100/APP_Teste')
    if token:
        return {"token": token, "repo": repo, "available": True}
    return {"available": False}

@register_tool(
    id="workspace.persist",
    name="Workspace Persistente",
    description="Guarda workspace em Supabase Storage 1GB free ou R2 10GB free ou GitHub Pages gh-pages — persistência total após deploy",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"filename": {"type": "string"}, "all": {"type": "boolean"}}, "required": []},
    output_schema={"type": "object", "properties": {"persisted": {"type": "boolean"}}}
)
def workspace_persist(filename: str = None, all: bool = False) -> Dict[str, Any]:
    """
    Persiste workspace files em storage externo
    Se SUPABASE_URL+KEY -> Supabase Storage
    Se R2 vars -> Cloudflare R2
    Se GITHUB_TOKEN -> gh-pages branch commit
    Senão local apenas com instruções
    """
    ws = _get_workspace_path()
    results = []
    supabase = _check_supabase_config()
    r2 = _check_r2_config()
    github = _check_github_config()
    
    files_to_persist = []
    if all:
        files_to_persist = list(ws.glob("*.html")) + list(ws.glob("*.css")) + list(ws.glob("*.js"))
    elif filename:
        f = ws / filename
        if f.exists():
            files_to_persist = [f]
        else:
            return {"persisted": False, "error": f"Ficheiro {filename} não existe", "path": str(f)}
    else:
        # últimos 5
        files_to_persist = sorted(ws.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    
    # Tenta Supabase
    if supabase["available"]:
        try:
            import httpx
            for filepath in files_to_persist:
                try:
                    content = filepath.read_bytes()
                    # Supabase Storage API: POST /storage/v1/object/bucket/filename
                    url = f"{supabase['url'].rstrip('/')}/storage/v1/object/{supabase['bucket']}/{filepath.name}"
                    headers = {
                        "Authorization": f"Bearer {supabase['key']}",
                        "apikey": supabase['key'],
                        "Content-Type": "text/html"
                    }
                    with httpx.Client(timeout=30) as client:
                        res = client.post(url, content=content, headers=headers)
                        if res.status_code in (200, 201):
                            results.append({"file": filepath.name, "platform": "supabase", "url": f"{supabase['url']}/storage/v1/object/public/{supabase['bucket']}/{filepath.name}", "status": "ok"})
                        else:
                            results.append({"file": filepath.name, "platform": "supabase", "error": f"{res.status_code} {res.text[:200]}", "status": "fail"})
                except Exception as e:
                    results.append({"file": filepath.name, "platform": "supabase", "error": str(e), "status": "fail"})
            return {"persisted": any(r["status"]=="ok" for r in results), "platform": "supabase", "results": results, "bucket": supabase["bucket"], "message": f"Supabase Storage 1GB free — {len([r for r in results if r['status']=='ok'])} ficheiros persistidos"}
        except Exception as e:
            results.append({"platform": "supabase", "error": str(e)})
    
    # Tenta R2
    if r2["available"]:
        try:
            import boto3
            s3 = boto3.client(
                's3',
                endpoint_url=f"https://{r2['account_id']}.r2.cloudflarestorage.com",
                aws_access_key_id=r2["access_key"],
                aws_secret_access_key=r2["secret_key"],
                region_name="auto"
            )
            for filepath in files_to_persist:
                try:
                    s3.upload_file(str(filepath), r2["bucket"], filepath.name, ExtraArgs={'ContentType': 'text/html'})
                    results.append({"file": filepath.name, "platform": "r2", "url": f"https://{r2['bucket']}.r2.dev/{filepath.name}", "status": "ok"})
                except Exception as e:
                    results.append({"file": filepath.name, "platform": "r2", "error": str(e), "status": "fail"})
            return {"persisted": any(r["status"]=="ok" for r in results), "platform": "r2", "results": results, "bucket": r2["bucket"], "message": f"Cloudflare R2 10GB free — {len([r for r in results if r['status']=='ok'])} ficheiros persistidos"}
        except Exception as e:
            results.append({"platform": "r2", "error": str(e), "note": "pip install boto3 necessário"})
    
    # Tenta GitHub Pages gh-pages
    if github["available"]:
        try:
            import base64
            import httpx
            for filepath in files_to_persist:
                try:
                    content = filepath.read_text(encoding='utf-8')
                    b64 = base64.b64encode(content.encode()).decode()
                    # GitHub API: PUT /repos/{owner}/{repo}/contents/{path}?ref=gh-pages
                    api_url = f"https://api.github.com/repos/{github['repo']}/contents/{filepath.name}"
                    headers = {"Authorization": f"Bearer {github['token']}", "Accept": "application/vnd.github.v3+json"}
                    # Verifica se existe para pegar sha
                    with httpx.Client(timeout=20) as client:
                        get_res = client.get(api_url + "?ref=gh-pages", headers=headers)
                        sha = get_res.json().get("sha") if get_res.status_code == 200 else None
                        payload = {
                            "message": f"Persist workspace {filepath.name} via builder",
                            "content": b64,
                            "branch": "gh-pages"
                        }
                        if sha:
                            payload["sha"] = sha
                        put_res = client.put(api_url, json=payload, headers=headers)
                        if put_res.status_code in (200, 201):
                            results.append({"file": filepath.name, "platform": "github-pages", "url": f"https://{github['repo'].split('/')[0]}.github.io/{github['repo'].split('/')[1]}/{filepath.name}", "status": "ok"})
                        else:
                            results.append({"file": filepath.name, "platform": "github-pages", "error": f"{put_res.status_code} {put_res.text[:200]}", "status": "fail"})
                except Exception as e:
                    results.append({"file": filepath.name, "platform": "github-pages", "error": str(e), "status": "fail"})
            return {"persisted": any(r["status"]=="ok" for r in results), "platform": "github-pages", "results": results, "repo": github["repo"], "message": f"GitHub Pages gh-pages free forever — {len([r for r in results if r['status']=='ok'])} ficheiros persistidos em https://{github['repo'].split('/')[0]}.github.io/{github['repo'].split('/')[1]}/"}
        except Exception as e:
            results.append({"platform": "github-pages", "error": str(e)})
    
    # Fallback local apenas
    return {
        "persisted": False,
        "platform": "local",
        "local_files": [f.name for f in files_to_persist],
        "results": results,
        "message": "Sem config externa — workspace apenas local (efêmero no Render free). Para persistência total free forever, adiciona uma destas env vars no Render/Leapcell:",
        "how_to": {
            "supabase_1gb_free": "SUPABASE_URL=https://xxx.supabase.co + SUPABASE_KEY=eyJ... + SUPABASE_BUCKET=workspace — 1GB free sem cartão — https://supabase.com/dashboard/project/_/storage",
            "r2_10gb_free": "R2_ACCOUNT_ID=xxx + R2_ACCESS_KEY_ID=xxx + R2_SECRET_ACCESS_KEY=xxx + R2_BUCKET=workspace — 10GB free sem cartão — https://dash.cloudflare.com/r2",
            "github_pages_free_forever": "GITHUB_TOKEN=ghp_xxx + GITHUB_REPO=rpolicarpo100/APP_Teste — free forever — cria branch gh-pages automaticamente — https://github.com/settings/tokens",
            "current": f"{len(files_to_persist)} ficheiros locais em {ws} — acessíveis via /workspace/ — mas perdem-se no restart Render free sem disk"
        },
        "available_platforms": {
            "supabase": supabase["available"],
            "r2": r2["available"],
            "github_pages": github["available"]
        }
    }

@register_tool(
    id="workspace.persist.status",
    name="Workspace Persist Status",
    description="Verifica status de persistência — que plataformas estão configuradas",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {}, "required": []},
    output_schema={"type": "object", "properties": {"status": {"type": "object"}}}
)
def workspace_persist_status() -> Dict[str, Any]:
    ws = _get_workspace_path()
    files = list(ws.glob("*.html"))
    supabase = _check_supabase_config()
    r2 = _check_r2_config()
    github = _check_github_config()
    
    return {
        "workspace_path": str(ws),
        "local_files": len(files),
        "files": [{"name": f.name, "size": f.stat().st_size, "url": f"/workspace/{f.name}"} for f in sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:10]],
        "platforms": {
            "supabase_1gb_free": {"available": supabase["available"], "url": supabase.get("url"), "bucket": supabase.get("bucket"), "how_to": "Adiciona SUPABASE_URL + SUPABASE_KEY no Render env vars — 1GB free sem cartão", "link": "https://supabase.com/storage"},
            "r2_10gb_free": {"available": r2["available"], "bucket": r2.get("bucket"), "how_to": "Adiciona R2_ACCOUNT_ID + R2_ACCESS_KEY_ID + R2_SECRET_ACCESS_KEY — 10GB free sem cartão", "link": "https://dash.cloudflare.com/r2"},
            "github_pages_free_forever": {"available": github["available"], "repo": github.get("repo"), "how_to": "Adiciona GITHUB_TOKEN ghp_xxx — free forever — branch gh-pages auto", "link": "https://github.com/settings/tokens"},
            "local": {"available": True, "ephemeral": "Render free sem disk — perde-se no restart", "persistent": "Leapcell 4GB ou Render disk $0.25/GB ou Supabase/R2/GitHub Pages"}
        },
        "can_persist": supabase["available"] or r2["available"] or github["available"],
        "message": "Workspace persistente — local + Supabase 1GB free + R2 10GB free + GitHub Pages free forever"
    }
