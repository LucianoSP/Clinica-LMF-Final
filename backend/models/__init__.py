# Arquivo __init__.py para marcar o diretório models como um pacote Python
from .paciente import Paciente
from .plano_saude import PlanoSaude
from .carteirinha import Carteirinha
from .guia import Guia

__all__ = ['Paciente', 'PlanoSaude']
