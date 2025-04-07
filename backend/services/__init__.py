# Arquivo __init__.py para marcar o diretório services como um pacote Python
from .paciente import PacienteService
from .plano_saude import PlanoSaudeService
from .carteirinha import CarteirinhaService
from .guia import GuiaService

__all__ = [PacienteService, PlanoSaudeService, CarteirinhaService]
