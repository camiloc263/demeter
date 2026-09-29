# D:\proyectos\Demeter\core_compartido\demeter_core\ai_client.py
"""Cliente asíncrono unificado para modelos de IA generativa (Claude, OpenAI, vLLM).

Los tres proveedores se hablan por HTTP puro con `httpx` (sin SDKs adicionales):
Anthropic usa su API de mensajes nativa; OpenAI y vLLM comparten el formato
"chat completions" (vLLM expone un servidor compatible con la API de OpenAI),
por lo que `ClienteVLLM` reutiliza la implementación de `ClienteOpenAI` y solo
cambia la URL base y la autenticación.

Uso típico dentro de un microservicio FastAPI:

    from demeter_core.ai_client import AIConfig, ProveedorIA, crear_cliente_ia

    config = AIConfig(proveedor=ProveedorIA.CLAUDE, api_key=settings.AI_API_KEY)
    async with crear_cliente_ia(config) as cliente:
        texto = await cliente.generar_texto("Resume el estado del corral 3")
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import httpx

logger = logging.getLogger("demeter_core.ai_client")


class ProveedorIA(str, Enum):
    """Proveedores de modelos de lenguaje soportados."""

    CLAUDE = "claude"
    OPENAI = "openai"
    VLLM = "vllm"


class AIClientError(RuntimeError):
    """El proveedor de IA no respondió correctamente tras agotar los reintentos."""


@dataclass(frozen=True)
class AIConfig:
    """Configuración de conexión y generación para un proveedor de IA."""

    proveedor: ProveedorIA
    api_key: str = ""
    modelo: str = ""
    base_url: str = ""
    timeout_segundos: float = 15.0
    max_reintentos: int = 2
    max_tokens: int = 512
    temperatura: float = 0.4


class BaseAIClient(ABC):
    """Interfaz común a cualquier proveedor: construye la petición HTTP, la
    envía con reintentos ante fallos transitorios (429/5xx/timeout) y extrae
    el texto de la respuesta. Las subclases solo definen el formato propio
    de cada proveedor.
    """

    def __init__(self, config: AIConfig, cliente_http: Optional[httpx.AsyncClient] = None):
        self._config = config
        self._cliente_http = cliente_http or httpx.AsyncClient(timeout=config.timeout_segundos)
        self._cliente_es_propio = cliente_http is None

    async def __aenter__(self) -> "BaseAIClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.cerrar()

    async def cerrar(self) -> None:
        """Libera el pool de conexiones si el cliente HTTP fue creado internamente."""
        if self._cliente_es_propio:
            await self._cliente_http.aclose()

    @abstractmethod
    def _construir_peticion(self, prompt: str, system: Optional[str]) -> tuple[str, dict, dict]:
        """Devuelve (url, headers, cuerpo_json) específicos del proveedor."""

    @abstractmethod
    def _extraer_texto(self, respuesta_json: dict) -> str:
        """Extrae el texto generado de la respuesta cruda del proveedor."""

    async def generar_texto(self, prompt: str, system: Optional[str] = None) -> str:
        """Genera texto a partir de `prompt` (y un `system` prompt opcional).

        Reintenta con backoff exponencial ante 429/5xx/timeout hasta
        `max_reintentos` veces; agota los intentos y levanta `AIClientError`
        si ninguno tiene éxito.
        """
        url, headers, body = self._construir_peticion(prompt, system)
        ultimo_error: Optional[Exception] = None

        for intento in range(self._config.max_reintentos + 1):
            try:
                respuesta = await self._cliente_http.post(url, headers=headers, json=body)
                if respuesta.status_code == 429 or respuesta.status_code >= 500:
                    respuesta.raise_for_status()
                respuesta.raise_for_status()
                return self._extraer_texto(respuesta.json())
            except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
                ultimo_error = exc
                if intento < self._config.max_reintentos:
                    espera = 2**intento * 0.5
                    logger.warning(
                        "Fallo al llamar al proveedor de IA '%s' (%s), reintentando en %.1fs",
                        self._config.proveedor.value,
                        exc,
                        espera,
                    )
                    await asyncio.sleep(espera)
                    continue
                break

        raise AIClientError(
            f"No se pudo obtener respuesta del proveedor '{self._config.proveedor.value}' "
            f"tras {self._config.max_reintentos + 1} intento(s)"
        ) from ultimo_error


class ClienteClaude(BaseAIClient):
    """Cliente para la API de mensajes de Anthropic (Claude)."""

    def _construir_peticion(self, prompt: str, system: Optional[str]) -> tuple[str, dict, dict]:
        url = f"{self._config.base_url or 'https://api.anthropic.com'}/v1/messages"
        headers = {
            "x-api-key": self._config.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": self._config.modelo or "claude-3-5-haiku-20241022",
            "max_tokens": self._config.max_tokens,
            "temperature": self._config.temperatura,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            body["system"] = system
        return url, headers, body

    def _extraer_texto(self, respuesta_json: dict) -> str:
        return "".join(bloque.get("text", "") for bloque in respuesta_json["content"])


class ClienteOpenAI(BaseAIClient):
    """Cliente para la API de Chat Completions de OpenAI."""

    def _construir_peticion(self, prompt: str, system: Optional[str]) -> tuple[str, dict, dict]:
        url = f"{self._config.base_url or 'https://api.openai.com/v1'}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._config.api_key}",
            "content-type": "application/json",
        }
        mensajes = []
        if system:
            mensajes.append({"role": "system", "content": system})
        mensajes.append({"role": "user", "content": prompt})
        body = {
            "model": self._config.modelo or "gpt-4o-mini",
            "max_tokens": self._config.max_tokens,
            "temperature": self._config.temperatura,
            "messages": mensajes,
        }
        return url, headers, body

    def _extraer_texto(self, respuesta_json: dict) -> str:
        return respuesta_json["choices"][0]["message"]["content"]


class ClienteVLLM(ClienteOpenAI):
    """Cliente para un servidor vLLM propio que expone una API compatible con
    OpenAI (`vllm serve ... `). Reutiliza el formato de petición/respuesta de
    `ClienteOpenAI`; solo cambia la URL base y la autenticación, que suele ser
    opcional en un despliegue interno.
    """

    def _construir_peticion(self, prompt: str, system: Optional[str]) -> tuple[str, dict, dict]:
        base_url = (self._config.base_url or "http://localhost:8000").rstrip("/")
        url = f"{base_url}/v1/chat/completions"
        headers = {"content-type": "application/json"}
        if self._config.api_key:
            headers["Authorization"] = f"Bearer {self._config.api_key}"
        mensajes = []
        if system:
            mensajes.append({"role": "system", "content": system})
        mensajes.append({"role": "user", "content": prompt})
        body = {
            "model": self._config.modelo or "default",
            "max_tokens": self._config.max_tokens,
            "temperature": self._config.temperatura,
            "messages": mensajes,
        }
        return url, headers, body


_CLASES_POR_PROVEEDOR: dict[ProveedorIA, type[BaseAIClient]] = {
    ProveedorIA.CLAUDE: ClienteClaude,
    ProveedorIA.OPENAI: ClienteOpenAI,
    ProveedorIA.VLLM: ClienteVLLM,
}


def crear_cliente_ia(config: AIConfig, cliente_http: Optional[httpx.AsyncClient] = None) -> BaseAIClient:
    """Fábrica: instancia el cliente concreto correspondiente a `config.proveedor`."""
    try:
        clase = _CLASES_POR_PROVEEDOR[config.proveedor]
    except KeyError as exc:
        raise ValueError(f"Proveedor de IA no soportado: {config.proveedor!r}") from exc
    return clase(config, cliente_http=cliente_http)
