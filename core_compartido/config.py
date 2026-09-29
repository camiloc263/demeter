# D:\proyectos\Demeter\core_compartido\config.py
"""Configuración compartida (variables de entorno) para los microservicios de Demeter."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from demeter_core.ai_client import ProveedorIA


class Settings(BaseSettings):
    # Configuración general del servicio
    SERVICE_NAME: str = Field("unnamed_service")
    SERVICE_PORT: int = 8000
    DB_URL: str = "sqlite:///./app.db"

    # URLs de otros servicios del ecosistema (opcional)
    CORRALES_URL: str = ""
    INVENTORY_URL: str = ""
    IOT_URL: str = ""
    USUARIOS_URL: str = ""
    IA_MODEL_PATH: str = ""

    # Cliente de IA generativa (Claude / OpenAI / vLLM) — ver demeter_core.ai_client
    AI_PROVIDER: ProveedorIA = ProveedorIA.CLAUDE
    AI_API_KEY: str = ""
    AI_MODEL: str = ""
    AI_BASE_URL: str = ""
    AI_TIMEOUT_SECONDS: float = 15.0
    AI_MAX_RETRIES: int = 2
    AI_MESSAGES_ENABLED: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)
