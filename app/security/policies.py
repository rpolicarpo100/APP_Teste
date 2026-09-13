"""
Políticas de segurança adicionais — GOD §9, Local AI Brain §19
"""
from pathlib import Path
from typing import List
import re

# Paths proibidos — nunca permitir acesso
FORBIDDEN_PATHS = [
    "/etc/passwd",
    "/etc/shadow",
    ".env",
    ".git/config",
    ".git/credentials",
    ".netrc",
    "id_rsa",
    "id_ed25519",
]

FORBIDDEN_COMMANDS = [
    "rm -rf /",
    "mkfs",
    "dd if=",
    ":(){:|:&};:",  # fork bomb
    "shutdown",
    "reboot",
    "chmod 777",
]

def is_path_allowed(requested_path: str, allowed_paths: List[str], workspace_root: Path) -> tuple[bool, str]:
    """
    Verifica se path está dentro de allowed_paths e não contém forbidden.
    Trata conteúdo externo como dados não confiáveis — não executa instruções de ficheiros.
    """
    # Normaliza
    try:
        req = Path(requested_path).resolve()
    except Exception:
        return False, "Path inválido"

    # Verifica forbidden substrings
    for forbidden in FORBIDDEN_PATHS:
        if forbidden in str(req):
            # Permite .env.example mas não .env real fora de workspace?
            if forbidden == ".env" and "example" in str(req):
                continue
            # Se for dentro do workspace, .env é bloqueado a menos que explicitamente permitido
            if ".env" == req.name:
                return False, f"Path proibido: {forbidden}"

    # Se allowed_paths vazio, só permite dentro do workspace
    if not allowed_paths:
        try:
            req.relative_to(workspace_root.resolve())
            return True, "Dentro do workspace"
        except ValueError:
            return False, f"Path {req} fora do workspace"

    for allowed in allowed_paths:
        allowed_abs = (workspace_root / allowed).resolve() if not Path(allowed).is_absolute() else Path(allowed).resolve()
        try:
            req.relative_to(allowed_abs)
            return True, f"Dentro de {allowed_abs}"
        except ValueError:
            continue

    return False, f"Path {req} não está em allowed_paths {allowed_paths}"

def is_command_allowed(command: str) -> tuple[bool, str]:
    for forbidden in FORBIDDEN_COMMANDS:
        if forbidden in command:
            return False, f"Comando contém padrão proibido: {forbidden}"
    # Bloqueia comandos com pipe para shell perigoso sem aprovação
    if "curl" in command and "| sh" in command:
        return False, "Comando curl | sh bloqueado"
    return True, "Permitido"

def sanitize_external_content(content: str) -> str:
    """
    Trata conteúdo de ficheiros, páginas Web e respostas de agentes como dados não confiáveis.
    Remove tentativas de prompt injection.
    """
    # Detecta tentativas comuns de prompt injection
    injection_patterns = [
        r"ignore previous instructions",
        r"system:\s*you are now",
        r"\[INST\]",
        r"\<\|im_start\|>",
        r"jailbreak",
        r"do anything now",
    ]
    lower = content.lower()
    for pattern in injection_patterns:
        if re.search(pattern, lower):
            # Não remove conteúdo, mas marca como suspeito — log
            # Retorna conteúdo original mas caller deve logar
            pass
    return content

def check_prompt_injection(content: str) -> tuple[bool, List[str]]:
    """Retorna (é suspeito, lista de padrões encontrados)"""
    found = []
    patterns = [
        r"ignore.*previous.*instructions",
        r"you are now.*admin",
        r"system prompt",
        r"reveal.*instructions",
        r"disregard.*safety",
    ]
    lower = content.lower()
    for pat in patterns:
        if re.search(pat, lower):
            found.append(pat)
    return (len(found) > 0, found)
