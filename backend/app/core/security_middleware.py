"""
Middleware de segurança para isolamento de dados entre assinantes (multitenant)
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, UserRole
from app.core.dependencies import get_current_user


async def check_subscriber_access(
    request: Request,
    subscriber_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Middleware que verifica se o usuário atual está acessando recursos do seu próprio assinante.
    
    Args:
        request: Requisição HTTP
        subscriber_id: ID do assinante que está sendo acessado
        current_user: Usuário autenticado atual
        db: Sessão do banco de dados
        
    Returns:
        bool: True se o acesso for permitido
        
    Raises:
        HTTPException: Se o acesso for negado
    """
    # Super admins e diretores têm acesso a todos os assinantes
    if current_user.role in [UserRole.SUPER_ADMIN, UserRole.DIRETOR]:
        return True
    
    # Verificar se o usuário possui um subscriber_id
    if not current_user.subscriber_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: usuário não está associado a nenhum assinante"
        )
    
    # Verificar se o subscriber_id do usuário corresponde ao assinante sendo acessado
    if str(current_user.subscriber_id) != str(subscriber_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: recurso pertence a outro assinante"
        )
    
    return True


def create_subscriber_access_dependency(param_name: str = "subscriber_id"):
    """
    Cria uma dependência que verifica o acesso a um assinante específico.
    
    Args:
        param_name: Nome do parâmetro de rota que contém o subscriber_id
        
    Returns:
        Função de dependência para verificar acesso ao assinante
    """
    async def verify_subscriber_access(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # Super admins e diretores têm acesso a todos os assinantes
        if current_user.role in [UserRole.SUPER_ADMIN, UserRole.DIRETOR]:
            return True
        
        # Extrair o subscriber_id da rota
        path_params = request.path_params
        path_subscriber_id = path_params.get(param_name)
        
        # Se o subscriber_id não estiver na rota, não aplicar verificação
        if not path_subscriber_id:
            return True
        
        # Verificar se o usuário possui um subscriber_id
        if not current_user.subscriber_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: usuário não está associado a nenhum assinante"
            )
        
        # Verificar se o subscriber_id do usuário corresponde ao assinante sendo acessado
        if str(current_user.subscriber_id) != str(path_subscriber_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: recurso pertence a outro assinante"
            )
        
        return True
    
    return verify_subscriber_access


# Função para uso em rotas que acessam recursos vinculados indiretamente a um assinante
async def verify_resource_subscriber_access(
    request: Request,
    resource_subscriber_id: Optional[UUID],
    current_user: User = Depends(get_current_user)
):
    """
    Verifica se o usuário pode acessar um recurso com base no subscriber_id associado ao recurso.
    
    Args:
        request: Requisição HTTP
        resource_subscriber_id: ID do assinante associado ao recurso
        current_user: Usuário autenticado atual
        
    Returns:
        bool: True se o acesso for permitido
        
    Raises:
        HTTPException: Se o acesso for negado
    """
    # Super admins e diretores têm acesso a todos os recursos
    if current_user.role in [UserRole.SUPER_ADMIN, UserRole.DIRETOR]:
        return True
    
    # Se o recurso não tiver subscriber_id, não aplicar verificação
    if not resource_subscriber_id:
        # Para recursos sem subscriber_id, considerar acesso público
        return True
    
    # Verificar se o usuário possui um subscriber_id
    if not current_user.subscriber_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: usuário não está associado a nenhum assinante"
        )
    
    # Verificar se o subscriber_id do usuário corresponde ao do recurso
    if str(current_user.subscriber_id) != str(resource_subscriber_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: recurso pertence a outro assinante"
        )
    
    return True