"""
Rotas da API para gerenciamento de usuários
"""

from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path, Request, Response
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserUpdate, UserResponse, PaginatedUserResponse
from app.services.user_service import UserService
from app.db.session import get_db
from app.db.models import UserRole, User
from app.core.dependencies import get_current_user, get_current_super_admin, get_current_admin_or_director

# Criar router para usuários
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Não encontrado"}},
)

@router.get("/", response_model=PaginatedUserResponse, status_code=status.HTTP_200_OK)
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Alterado para permitir que todos os usuários vejam a lista, mas filtrada
    skip: int = Query(0, ge=0, description="Quantos usuários pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de usuários retornados"),
    name: Optional[str] = Query(None, description="Filtrar por nome"),
    email: Optional[str] = Query(None, description="Filtrar por email"),
    role: Optional[UserRole] = Query(None, description="Filtrar por role"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status de ativação")
):
    """
    Listar todos os usuários com opções de paginação e filtros.
    Usuários com papéis diferentes de SUPER_ADMIN e DIRETOR só podem ver usuários do seu próprio assinante.
    """
    # Montar filtros
    filters = {}
    if name:
        filters["name"] = name
    if email:
        filters["email"] = email
    if role:
        filters["role"] = role
    if is_active is not None:
        filters["is_active"] = is_active
    
    return UserService.get_users(db, skip=skip, limit=limit, filter_params=filters, current_user=current_user)

@router.get("/me", response_model=None, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Obter dados do usuário atual autenticado.
    Se não houver autenticação, a dependência get_current_user tratará o erro,
    retornando um status 200 com informações de que o usuário não está autenticado.
    """
    # Se chegou aqui, o usuário está autenticado (a dependência não lançou exceção)
    # e current_user contém o objeto do usuário
    return current_user


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int = Path(..., description="ID do usuário"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obter um usuário pelo ID.
    Usuários com papéis diferentes de SUPER_ADMIN e DIRETOR só podem ver usuários do seu próprio assinante.
    """
    # O isolamento por subscriber_id é aplicado dentro do service
    user = UserService.get_user_by_id(db, user_id, current_user=current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Criar um novo usuário.
    Usuários com papel DONO_ASSINANTE só podem criar usuários associados ao seu próprio assinante.
    SUPER_ADMIN e DIRETOR podem criar usuários para qualquer assinante.
    """
    # Verificar permissões - apenas SUPER_ADMIN, DIRETOR ou DONO_ASSINANTE podem criar usuários
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.DIRETOR, UserRole.DONO_ASSINANTE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada. Apenas administradores, diretores ou donos de assinante podem criar usuários."
        )
    
    # Se for DONO_ASSINANTE, garantir que o usuário criado esteja vinculado ao mesmo assinante
    if current_user.role == UserRole.DONO_ASSINANTE:
        if not current_user.subscriber_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada. Você não está associado a nenhum assinante."
            )
        
        # Se o subscriber_id for fornecido, verificar se corresponde ao do usuário atual
        if user_data.subscriber_id and str(user_data.subscriber_id) != str(current_user.subscriber_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada. Você só pode criar usuários para seu próprio assinante."
            )
        
        # Garantir que o subscriber_id seja definido
        user_data.subscriber_id = current_user.subscriber_id
    
    return UserService.create_user(db, user_data)

@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_data: UserUpdate,
    user_id: int = Path(..., description="ID do usuário"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualizar um usuário existente.
    Usuários com papel DONO_ASSINANTE só podem atualizar usuários do seu próprio assinante.
    SUPER_ADMIN e DIRETOR podem atualizar usuários de qualquer assinante.
    """
    # Verificar permissões - apenas SUPER_ADMIN, DIRETOR ou DONO_ASSINANTE podem atualizar usuários
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.DIRETOR, UserRole.DONO_ASSINANTE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada. Apenas administradores, diretores ou donos de assinante podem atualizar usuários."
        )
    
    # Obter o usuário a ser atualizado (com filtragem por subscriber_id já aplicada)
    user_to_update = UserService.get_user_by_id(db, user_id, current_user=current_user)
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado ou você não tem permissão para acessá-lo"
        )
    
    # Se tentar atualizar subscriber_id, verificar permissões
    if user_data.subscriber_id is not None and current_user.role == UserRole.DONO_ASSINANTE:
        if str(user_data.subscriber_id) != str(current_user.subscriber_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada. Você só pode definir usuários para seu próprio assinante."
            )
    
    updated_user = UserService.update_user(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erro ao atualizar usuário"
        )
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int = Path(..., description="ID do usuário"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Desativar ou excluir um usuário.
    Usuários com papel DONO_ASSINANTE só podem remover usuários do seu próprio assinante.
    SUPER_ADMIN e DIRETOR podem remover usuários de qualquer assinante.
    """
    # Verificar permissões - apenas SUPER_ADMIN, DIRETOR ou DONO_ASSINANTE podem remover usuários
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.DIRETOR, UserRole.DONO_ASSINANTE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada. Apenas administradores, diretores ou donos de assinante podem remover usuários."
        )
    
    # Obter o usuário a ser removido (com filtragem por subscriber_id já aplicada)
    user_to_delete = UserService.get_user_by_id(db, user_id, current_user=current_user)
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado ou você não tem permissão para acessá-lo"
        )
    
    # DONO_ASSINANTE não pode excluir a si mesmo
    if current_user.role == UserRole.DONO_ASSINANTE and current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada. Você não pode remover sua própria conta."
        )
    
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erro ao remover usuário"
        )
    return None


@router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int = Path(..., description="ID do usuário"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ativar um usuário.
    Usuários com papel DONO_ASSINANTE só podem ativar usuários do seu próprio assinante.
    SUPER_ADMIN e DIRETOR podem ativar usuários de qualquer assinante.
    """
    # Verificar permissões - apenas SUPER_ADMIN, DIRETOR ou DONO_ASSINANTE podem ativar usuários
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.DIRETOR, UserRole.DONO_ASSINANTE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada. Apenas administradores, diretores ou donos de assinante podem ativar usuários."
        )
    
    # Obter o usuário a ser ativado (com filtragem por subscriber_id já aplicada)
    user_to_activate = UserService.get_user_by_id(db, user_id, current_user=current_user)
    if not user_to_activate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado ou você não tem permissão para acessá-lo"
        )
    
    updated_user = UserService.toggle_user_status(db, user_id, activate=True)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erro ao ativar usuário"
        )
    return updated_user


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int = Path(..., description="ID do usuário"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Desativar um usuário.
    Usuários com papel DONO_ASSINANTE só podem desativar usuários do seu próprio assinante.
    SUPER_ADMIN e DIRETOR podem desativar usuários de qualquer assinante.
    """
    # Verificar permissões - apenas SUPER_ADMIN, DIRETOR ou DONO_ASSINANTE podem desativar usuários
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.DIRETOR, UserRole.DONO_ASSINANTE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada. Apenas administradores, diretores ou donos de assinante podem desativar usuários."
        )
    
    # Obter o usuário a ser desativado (com filtragem por subscriber_id já aplicada)
    user_to_deactivate = UserService.get_user_by_id(db, user_id, current_user=current_user)
    if not user_to_deactivate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado ou você não tem permissão para acessá-lo"
        )
    
    # DONO_ASSINANTE não pode desativar a si mesmo
    if current_user.role == UserRole.DONO_ASSINANTE and current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada. Você não pode desativar sua própria conta."
        )
    
    updated_user = UserService.toggle_user_status(db, user_id, activate=False)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erro ao desativar usuário"
        )
    return updated_user