"""
Utilitários para verificação de permissões nas rotas da API
"""

from functools import wraps
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.role_hierarchy import get_permissions_for_role, has_permission
from app.db.models import User
from app.db.session import get_db


def user_has_permissions(
    user: User,
    required_permissions: List[str],
    require_all: bool = True
) -> bool:
    """
    Verifica se o usuário tem as permissões necessárias.
    
    Args:
        user: Usuário a ser verificado
        required_permissions: Lista de permissões necessárias
        require_all: Se True, o usuário precisa ter todas as permissões,
                    se False, basta ter pelo menos uma
    
    Returns:
        bool: True se o usuário tem as permissões necessárias, False caso contrário
    """
    if not user or not required_permissions:
        return False
    
    # Super admin tem todas as permissões
    if user.role and user.role.value in ["SUPER_ADMIN", "DIRETOR"]:
        return True
    
    # Obtém permissões do papel (role) do usuário
    role_permissions = get_permissions_for_role(user.role)
    
    # Obtém permissões personalizadas do usuário
    custom_permissions = user.permissions if hasattr(user, 'permissions') else []
    
    # Combina todas as permissões
    all_permissions = set(role_permissions + custom_permissions)
    
    if require_all:
        # Usuário deve ter todas as permissões requeridas
        return all(perm in all_permissions for perm in required_permissions)
    else:
        # Usuário deve ter pelo menos uma das permissões requeridas
        return any(perm in all_permissions for perm in required_permissions)


def has_required_permissions(
    required_permissions: List[str], 
    require_all: bool = True
):
    """
    Decorator para verificar se o usuário tem as permissões necessárias para acessar uma rota.
    
    Args:
        required_permissions: Lista de permissões necessárias
        require_all: Se True, o usuário precisa ter todas as permissões,
                    se False, basta ter pelo menos uma
    
    Returns:
        Uma dependência FastAPI que verifica as permissões
    """
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not user_has_permissions(current_user, required_permissions, require_all):
            permission_msg = " e ".join(required_permissions) if require_all else " ou ".join(required_permissions)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Você precisa ter permissão de {permission_msg}."
            )
        return current_user
    
    return Depends(dependency)


def has_permission(permission: str):
    """
    Shorthand para verificar uma única permissão.
    
    Args:
        permission: A permissão necessária
    
    Returns:
        Uma dependência FastAPI que verifica a permissão
    """
    return has_required_permissions([permission], require_all=True)


def has_any_permission(permissions: List[str]):
    """
    Shorthand para verificar se o usuário tem pelo menos uma das permissões listadas.
    
    Args:
        permissions: Lista de permissões, das quais o usuário precisa ter pelo menos uma
    
    Returns:
        Uma dependência FastAPI que verifica as permissões
    """
    return has_required_permissions(permissions, require_all=False)