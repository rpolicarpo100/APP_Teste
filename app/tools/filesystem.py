"""
Filesystem tools — leitura/escrita controlada
Conforme GOD §10 e Local AI Brain §12
"""
from pathlib import Path
from typing import List
import os

from app.tools.registry import register_tool
from app.config.settings import settings, ROOT_DIR
from app.security.policies import is_path_allowed, sanitize_external_content

def _resolve_workspace_path(path: str) -> Path:
    """Resolve path dentro do workspace permitido — tenta workspace, documents, e ROOT para leitura de código"""
    if os.path.isabs(path):
        p = Path(path)
    else:
        # Tenta workspace, depois documents, depois ROOT_DIR (para leitura de código)
        workspace_root = ROOT_DIR / settings.workspace_path
        p = workspace_root / path
        if not p.exists():
            docs_root = ROOT_DIR / settings.documents_path
            alt = docs_root / path
            if alt.exists():
                p = alt
            else:
                # Tenta ROOT_DIR / path (para app/, etc) — apenas para leitura
                alt2 = ROOT_DIR / path
                if alt2.exists():
                    p = alt2
    return p.resolve()

@register_tool(
    id="filesystem.read",
    name="Filesystem Read",
    description="Leitura controlada de ficheiros dentro do workspace",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    output_schema={"type": "object", "properties": {"content": {"type": "string"}, "path": {"type": "string"}}}
)
def filesystem_read(path: str) -> dict:
    """Lê ficheiro — implementação verificável"""
    workspace_root = ROOT_DIR
    # Para leitura, permite também app/ (código) além de workspace/docs/memory — mas bloqueia sensíveis
    allowed = [settings.workspace_path, settings.documents_path, settings.memory_path, "app"]
    
    # Verifica permissão
    from app.security.policies import FORBIDDEN_PATHS
    for forbidden in FORBIDDEN_PATHS:
        if forbidden in path and "example" not in path:
            if Path(path).name == ".env":
                return {"error": f"Acesso negado a {forbidden}", "content": None, "path": path}

    resolved = _resolve_workspace_path(path)
    
    # Valida allowed
    is_allowed, reason = is_path_allowed(str(resolved), allowed, workspace_root)
    if not is_allowed:
        return {"error": f"Acesso negado: {reason}", "content": None, "path": str(resolved)}

    if not resolved.exists():
        return {"error": f"Ficheiro não existe: {resolved}", "content": None, "path": str(resolved)}

    if resolved.is_dir():
        # Lista diretório
        files = [str(p.relative_to(workspace_root)) for p in resolved.iterdir()]
        return {"content": f"Diretório {resolved} contém: {', '.join(files[:50])}", "path": str(resolved), "is_dir": True, "files": files}

    try:
        # Limita tamanho a 1MB para MVP
        if resolved.stat().st_size > 1024*1024:
            return {"error": "Ficheiro demasiado grande (>1MB)", "content": None, "path": str(resolved)}
        content = resolved.read_text(encoding="utf-8", errors="ignore")
        # Trata como dados não confiáveis
        content = sanitize_external_content(content)
        return {"content": content, "path": str(resolved), "size": len(content)}
    except Exception as e:
        return {"error": str(e), "content": None, "path": str(resolved)}

@register_tool(
    id="filesystem.write",
    name="Filesystem Write",
    description="Escrita controlada de ficheiros dentro do workspace",
    risk_level="MEDIUM",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]},
    output_schema={"type": "object", "properties": {"path": {"type": "string"}, "written": {"type": "boolean"}}}
)
def filesystem_write(path: str, content: str) -> dict:
    workspace_root = ROOT_DIR
    allowed = [settings.workspace_path, settings.documents_path, settings.memory_path]

    resolved = _resolve_workspace_path(path)
    # Se não existe, resolve relativo a workspace
    if not resolved.parent.exists():
        # Cria parent se dentro do workspace
        try:
            # Verifica se parent estaria dentro de allowed
            is_allowed_parent, _ = is_path_allowed(str(resolved.parent), allowed, workspace_root)
            if not is_allowed_parent:
                return {"error": f"Parent não permitido: {resolved.parent}", "written": False, "path": str(resolved)}
            resolved.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return {"error": str(e), "written": False, "path": str(resolved)}

    is_allowed, reason = is_path_allowed(str(resolved), allowed, workspace_root)
    if not is_allowed:
        return {"error": f"Acesso negado: {reason}", "written": False, "path": str(resolved)}

    if not settings.allow_file_write:
        return {"error": "Escrita desabilitada por configuração", "written": False, "path": str(resolved)}

    try:
        resolved.write_text(content, encoding="utf-8")
        return {"path": str(resolved), "written": True, "size": len(content)}
    except Exception as e:
        return {"error": str(e), "written": False, "path": str(resolved)}

@register_tool(
    id="filesystem.list",
    name="Filesystem List",
    description="Lista ficheiros no workspace",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
    output_schema={"type": "object", "properties": {"files": {"type": "array"}}}
)
def filesystem_list(path: str = "") -> dict:
    workspace_root = ROOT_DIR / settings.workspace_path
    if path:
        target = workspace_root / path
    else:
        target = workspace_root
    try:
        if not target.exists():
            return {"files": [], "path": str(target), "error": "Não existe"}
        files = []
        for p in target.rglob("*"):
            if p.is_file():
                rel = p.relative_to(ROOT_DIR)
                files.append(str(rel))
        return {"files": files[:200], "count": len(files), "path": str(target)}
    except Exception as e:
        return {"error": str(e), "files": []}
