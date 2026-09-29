# D:\proyectos\Demeter\core_compartido\demeter_core\__init__.py
from .enums import EtapaCorral
from .esquemas import DatosClimaPayload, AlertaWhatsAppPayload
from .ai_client import AIClientError, AIConfig, BaseAIClient, ProveedorIA, crear_cliente_ia
from .auth import JWT_ALGORITHM, JWT_SECRET_KEY, UsuarioToken, obtener_usuario_actual, requiere_rol, verificar_token

__version__ = "0.1.0"

__all__ = [
    "EtapaCorral",
    "DatosClimaPayload",
    "AlertaWhatsAppPayload",
    "AIClientError",
    "AIConfig",
    "BaseAIClient",
    "ProveedorIA",
    "crear_cliente_ia",
    "JWT_ALGORITHM",
    "JWT_SECRET_KEY",
    "UsuarioToken",
    "obtener_usuario_actual",
    "requiere_rol",
    "verificar_token",
]