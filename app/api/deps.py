"""
Dependências para as rotas da API.
"""
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.db.session import get_db
from app.db.models.user import User
from app.core.security import ALGORITHM, SECRET_KEY
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    auto_error=False  # Não lança exceção automaticamente
)

def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """
    Valida o token JWT e retorna o usuário correspondente.
    
    Args:
        db: Sessão do banco de dados
        token: Token JWT
        
    Returns:
        Optional[User]: Usuário autenticado, None se o token for inválido
        
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        if token_data.sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    user = db.query(User).filter(User.id == token_data.sub).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifica se o usuário está ativo.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        User: Usuário ativo
        
    Raises:
        HTTPException: Se o usuário estiver inativo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
        
    return current_user

def check_permission(user: User, permission_name: str) -> bool:
    """
    Verifica se o usuário tem a permissão especificada.
    
    Args:
        user: Usuário a verificar
        permission_name: Nome da permissão
        
    Returns:
        bool: True se o usuário tem a permissão
        
    Raises:
        HTTPException: Se o usuário não tiver a permissão
    """
    # Super admins têm todas as permissões
    if user.role == "SUPER_ADMIN":
        return True
        
    # Verificar permissões personalizadas do usuário
    if user.permissions and permission_name in user.permissions:
        return user.permissions[permission_name]
        
    # Permissões padrão baseadas em função (considerar uma implementação real com base no seu sistema)
    role_permissions = {
        "DIRETOR": [
            "CAN_VIEW_INSUMO", "CAN_CREATE_INSUMO", "CAN_UPDATE_INSUMO", "CAN_DELETE_INSUMO"
        ],
        "COLABORADOR_NIVEL_2": [
            "CAN_VIEW_INSUMO", "CAN_CREATE_INSUMO", "CAN_UPDATE_INSUMO"
        ],
        "DONO_ASSINANTE": [
            "CAN_VIEW_INSUMO", "CAN_CREATE_INSUMO", "CAN_UPDATE_INSUMO", "CAN_DELETE_INSUMO"
        ]
    }
    
    if user.role in role_permissions and permission_name in role_permissions[user.role]:
        return True
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Permissão negada: {permission_name}"
    )