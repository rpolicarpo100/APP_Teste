"""
Python execution tool — controlado e com timeout
Conforme GOD §9 segurança
"""
from app.tools.registry import register_tool
from app.config.settings import settings
import subprocess
import tempfile
import os
from pathlib import Path

@register_tool(
    id="python.execute",
    name="Python Execute",
    description="Executa código Python isolado com timeout (requer aprovação se risco HIGH)",
    risk_level="HIGH",
    requires_approval=True,
    input_schema={"type": "object", "properties": {"code": {"type": "string"}, "timeout": {"type": "integer"}}, "required": ["code"]},
    output_schema={"type": "object", "properties": {"stdout": {"type": "string"}, "stderr": {"type": "string"}}}
)
def python_execute(code: str, timeout: int = 10) -> dict:
    if not settings.allow_python_exec:
        return {"error": "Execução Python desabilitada por configuração", "stdout": "", "stderr": "", "executed": False}

    # Limita timeout ao configurado
    timeout = min(timeout, settings.tool_timeout)

    # Escreve código temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(code)
        temp_path = f.name

    try:
        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(Path(settings.workspace_path))
        )
        return {
            "stdout": result.stdout[:10000],
            "stderr": result.stderr[:10000],
            "returncode": result.returncode,
            "executed": True,
            "timeout": timeout
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Timeout após {timeout}s", "stdout": "", "stderr": "", "executed": False}
    except Exception as e:
        return {"error": str(e), "stdout": "", "stderr": "", "executed": False}
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass
