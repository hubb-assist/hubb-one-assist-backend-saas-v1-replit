"""
Dependências para as rotas da API.
"""
from typing import Generator, Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import os

from app.db.session import get_db
from app.db.models.user import User
from app.core.security import ALGORITHM, oauth2_scheme

API_SECRET_KEY = os.environ.get("API_SECRET_KEY", "development_secret_key")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Obtém o usuário atualmente autenticado.
    
    Args:
        db: Sessão do banco de dados
        token: Token JWT de autenticação
        
    Returns:
        User: Usuário autenticado
        
    Raises:
        HTTPException: Se o token for inválido ou o usuário não for encontrado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar token
        payload = jwt.decode(token, API_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Buscar usuário no banco de dados
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verifica se o usuário está ativo.
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        User: Usuário ativo
        
    Raises:
        HTTPException: Se o usuário estiver inativo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo",
        )
    return current_user


def check_permission(user: User, permission_name: str) -> bool:
    """
    Verifica se o usuário tem uma permissão específica.
    
    Args:
        user: Usuário para verificar a permissão
        permission_name: Nome da permissão a ser verificada
        
    Returns:
        bool: True se o usuário tem a permissão, False caso contrário
    """
    # Super admin tem todas as permissões
    if user.role == "SUPER_ADMIN":
        return True
    
    # Verificar nas permissões do usuário
    for permission in user.permissions:
        if permission.name == permission_name and permission.active:
            return True
    
    return False