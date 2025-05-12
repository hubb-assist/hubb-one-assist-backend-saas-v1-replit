"""
Dependências para injeção em rotas e outros componentes
"""

from typing import Optional, Any

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, UserRole
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.schemas.auth import TokenData


async def get_token_data(request: Request) -> Optional[TokenData]:
    """
    Extrai e valida os dados do token JWT do cookie
    
    Args:
        request: Requisição HTTP
        
    Returns:
        Optional[TokenData]: Dados do token ou None
    """
    return AuthService.get_token_data_from_request(request)


async def get_current_user(
    request: Request,
    token_data: Optional[TokenData] = Depends(get_token_data),
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtém o usuário autenticado atual
    
    Args:
        request: Requisição HTTP
        token_data: Dados extraídos do token
        db: Sessão do banco de dados
        
    Returns:
        User: Usuário autenticado
        
    Raises:
        HTTPException: Se o usuário não estiver autenticado ou for inválido
    """
    # Verificar se é a rota /users/me e se não há token
    if token_data is None:
        # Para a rota /users/me, tratamento especial
        if request.url.path == "/users/me":
            # Importar aqui para evitar problemas de circular import
            from fastapi.responses import JSONResponse
            # Retornar 200 com informações de usuário não autenticado
            return JSONResponse(
                status_code=status.HTTP_200_OK, 
                content={"authenticated": False, "status": "not_authenticated", "message": "Usuário não autenticado"}
            )
        else:
            # Para outras rotas, manter o padrão 401
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Não autenticado",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    user = UserService.get_user_by_id(db, token_data.user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inválido",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


async def get_current_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifica se o usuário atual é um SUPER_ADMIN
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        User: Usuário autenticado com permissão de SUPER_ADMIN
        
    Raises:
        HTTPException: Se o usuário não tiver permissão de SUPER_ADMIN
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return current_user


async def get_current_admin_or_director(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifica se o usuário atual é um SUPER_ADMIN ou DIRETOR
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        User: Usuário autenticado com permissão de SUPER_ADMIN ou DIRETOR
        
    Raises:
        HTTPException: Se o usuário não tiver permissão adequada
    """
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.DIRETOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return current_user


def apply_subscriber_filter(query, model, current_user: User, admin_override: bool = True):
    """
    Aplica filtro por subscriber_id nas consultas, exceto para SUPER_ADMIN e DIRETOR (se admin_override=True)
    
    Args:
        query: Query SQLAlchemy para aplicar o filtro
        model: Modelo SQLAlchemy que deve conter o campo subscriber_id
        current_user: Usuário autenticado atual
        admin_override: Se True, não aplica filtro para SUPER_ADMIN e DIRETOR
        
    Returns:
        Query filtrada
    """
    # Se o usuário for SUPER_ADMIN ou DIRETOR e admin_override for True, não aplicar filtro
    if admin_override and current_user.role in [UserRole.SUPER_ADMIN, UserRole.DIRETOR]:
        return query
        
    # Se o usuário for DONO_ASSINANTE, aplicar filtro pelo seu subscriber_id
    if current_user.subscriber_id:
        # Verificar se o modelo tem o campo subscriber_id
        if hasattr(model, 'subscriber_id'):
            return query.filter(model.subscriber_id == current_user.subscriber_id)
    
    # Caso o usuário não tenha subscriber_id, retornar query vazia (segurança)
    if current_user.role == UserRole.DONO_ASSINANTE and not current_user.subscriber_id:
        # No SQLAlchemy, filter(False) resulta em uma query que não retorna resultados
        return query.filter(False)
        
    return query