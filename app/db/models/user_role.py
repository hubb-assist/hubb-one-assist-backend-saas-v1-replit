"""
Enum para definição de papéis do usuário.
"""
from enum import Enum as PyEnum

class UserRole(str, PyEnum):
    """Enum para roles de usuário no sistema"""
    SUPER_ADMIN = "SUPER_ADMIN"
    DIRETOR = "DIRETOR"
    COLABORADOR_NIVEL_2 = "COLABORADOR_NIVEL_2"
    DONO_ASSINANTE = "DONO_ASSINANTE"