# D:\proyectos\Demeter\tests\test_ai_client.py
"""Pruebas del cliente asíncrono de IA generativa (demeter_core.ai_client)."""

import os
import sys
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core_compartido")))

from demeter_core.ai_client import (  # noqa: E402
    AIClientError,
    AIConfig,
    ProveedorIA,
    crear_cliente_ia,
)


def _respuesta_mock(status_code: int, json_data: dict) -> MagicMock:
    respuesta = MagicMock(spec=httpx.Response)
    respuesta.status_code = status_code
    respuesta.json.return_value = json_data
    if status_code >= 400:
        respuesta.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=respuesta
        )
    else:
        respuesta.raise_for_status.return_value = None
    return respuesta


@pytest.mark.asyncio
async def test_claude_extrae_texto_correctamente():
    cliente_http = AsyncMock()
    cliente_http.post.return_value = _respuesta_mock(
        200, {"content": [{"type": "text", "text": "Hola "}, {"type": "text", "text": "mundo"}]}
    )
    cliente = crear_cliente_ia(AIConfig(proveedor=ProveedorIA.CLAUDE, api_key="k"), cliente_http=cliente_http)

    texto = await cliente.generar_texto("hola")

    assert texto == "Hola mundo"
    cliente_http.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_openai_extrae_texto_correctamente():
    cliente_http = AsyncMock()
    cliente_http.post.return_value = _respuesta_mock(
        200, {"choices": [{"message": {"content": "respuesta openai"}}]}
    )
    cliente = crear_cliente_ia(AIConfig(proveedor=ProveedorIA.OPENAI, api_key="k"), cliente_http=cliente_http)

    texto = await cliente.generar_texto("hola", system="eres útil")

    assert texto == "respuesta openai"


@pytest.mark.asyncio
async def test_vllm_usa_url_base_propia_sin_requerir_api_key():
    cliente_http = AsyncMock()
    cliente_http.post.return_value = _respuesta_mock(
        200, {"choices": [{"message": {"content": "respuesta local"}}]}
    )
    cliente = crear_cliente_ia(
        AIConfig(proveedor=ProveedorIA.VLLM, base_url="http://localhost:9000"), cliente_http=cliente_http
    )

    texto = await cliente.generar_texto("hola")

    assert texto == "respuesta local"
    url_llamada = cliente_http.post.call_args.args[0]
    assert url_llamada == "http://localhost:9000/v1/chat/completions"


@pytest.mark.asyncio
async def test_reintenta_ante_error_5xx_y_luego_funciona():
    cliente_http = AsyncMock()
    cliente_http.post.side_effect = [
        _respuesta_mock(503, {}),
        _respuesta_mock(200, {"choices": [{"message": {"content": "ok tras reintento"}}]}),
    ]
    cliente = crear_cliente_ia(
        AIConfig(proveedor=ProveedorIA.OPENAI, api_key="k", max_reintentos=2), cliente_http=cliente_http
    )

    texto = await cliente.generar_texto("hola")

    assert texto == "ok tras reintento"
    assert cliente_http.post.await_count == 2


@pytest.mark.asyncio
async def test_agota_reintentos_y_levanta_aiclienterror():
    cliente_http = AsyncMock()
    cliente_http.post.return_value = _respuesta_mock(500, {})
    cliente = crear_cliente_ia(
        AIConfig(proveedor=ProveedorIA.OPENAI, api_key="k", max_reintentos=1), cliente_http=cliente_http
    )

    with pytest.raises(AIClientError):
        await cliente.generar_texto("hola")

    assert cliente_http.post.await_count == 2  # intento inicial + 1 reintento


def test_proveedor_no_soportado_levanta_value_error():
    with pytest.raises(ValueError):
        crear_cliente_ia(AIConfig(proveedor="inexistente"))  # type: ignore[arg-type]
