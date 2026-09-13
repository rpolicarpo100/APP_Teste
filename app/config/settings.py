"""
GOD — Cerebro Core / Local AI Brain — Configurações
VERIFICADO: Implementação baseada em pydantic-settings, conforme spec Local AI Brain §23 e GOD §5
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os
from pathlib import Path

# Root dir = ai-brain/
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    app_name: str = Field(default="AI Brain - GOD Cerebro Core")
    app_env: str = Field(default="development")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)
    # Render e outros PaaS usam PORT
    port: Optional[int] = Field(default=None)  # fallback para PORT env

    ollama_host: str = Field(default="http://127.0.0.1:11434")
    ollama_model: str = Field(default="qwen3:8b")
    ollama_timeout: int = Field(default=60)

    database_url: str = Field(default="sqlite:///./data/brain.db")

    autonomy_level: int = Field(default=2, ge=0, le=4)

    max_agent_steps: int = Field(default=20)
    max_tool_calls: int = Field(default=50)
    tool_timeout: int = Field(default=30)

    workspace_path: str = Field(default="./data/workspace")
    documents_path: str = Field(default="./data/documents")
    log_path: str = Field(default="./data/logs")
    memory_path: str = Field(default="./data/memory")

    secret_key: str = Field(default="change-me")
    cors_origins: str = Field(default="*")

    allow_file_write: bool = Field(default=True)
    allow_python_exec: bool = Field(default=False)
    require_approval_for_high_risk: bool = Field(default=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    @property
    def effective_port(self) -> int:
        # Render define PORT, usa se APP_PORT não setado ou se PORT env existe
        import os
        port_env = os.getenv('PORT')
        if port_env:
            try:
                return int(port_env)
            except:
                pass
        if self.port:
            return self.port
        return self.app_port

    def get_cors_origins_list(self) -> List[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",")]

    def resolve_paths(self):
        """Garante que paths existem — PROPOSTA inicial para v1.0"""
        for p in [self.workspace_path, self.documents_path, self.log_path, self.memory_path]:
            abs_path = ROOT_DIR / p if not os.path.isabs(p) else Path(p)
            abs_path.mkdir(parents=True, exist_ok=True)

settings = Settings()
