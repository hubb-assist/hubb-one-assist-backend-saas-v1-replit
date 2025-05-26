"""
Rotas da API para autenticação de usuários
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, UserRole, Segment
from app.core.dependencies import get_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import Token, LoginRequest, RefreshTokenRequest, DashboardTypeResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=dict)
async def login(
    response: Response,
    user_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Autentica um usuário e retorna tokens JWT e informações de usuário
    """
    # Autenticar usuário
    user = AuthService.authenticate_user(db, user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Gerar tokens
    tokens = AuthService.create_login_tokens(user)
    
    # Configurar cookies
    AuthService.set_auth_cookies(response, tokens)
    
    # Informações sobre o usuário para ajudar no redirecionamento frontend
    segment_id = None
    if user.subscriber_id and user.subscriber:
        segment_id = str(user.subscriber.segment_id) if user.subscriber.segment_id else None
    
    # Resposta de sucesso com informações adicionais
    return {
        "mensagem": "Login realizado com sucesso.",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value if user.role else None,
            "subscriber_id": str(user.subscriber_id) if user.subscriber_id else None,
            "segment_id": segment_id
        }
    }


@router.post("/refresh-token", response_model=dict)
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Gera um novo access token a partir do refresh token
    """
    # Obter refresh token do cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token não fornecido",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Gerar novos tokens
    tokens = AuthService.refresh_access_token(refresh_token, db)
    
    # Configurar cookies
    AuthService.set_auth_cookies(response, tokens)
    
    return {"mensagem": "Token atualizado com sucesso."}


@router.post("/logout", response_model=dict)
async def logout(response: Response):
    """
    Encerra a sessão do usuário removendo os cookies
    """
    # Limpar cookies de autenticação
    AuthService.clear_auth_cookies(response)
    
    return {"mensagem": "Logout realizado com sucesso."}


@router.get("/dashboard-type", response_model=DashboardTypeResponse)
async def get_dashboard_type(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna o tipo de dashboard apropriado com base no papel (role) e segmento do usuário.
    
    Regras:
    - SUPER_ADMIN ou DIRETOR: admin_global
    - DONO_CLINICA com segment_id para veterinária: clinica_veterinaria
    - DONO_CLINICA com segment_id para odontologia: clinica_odontologica
    - DONO_CLINICA com outros segmentos: clinica_padrao
    - Outros papéis (DENTISTA, VETERINARIO, etc.): usuario_clinica
    """
    # Variável para armazenar o tipo de dashboard
    dashboard_type = "clinica_padrao"  # Valor padrão
    
    # Verificar o papel do usuário
    if current_user.role in [UserRole.SUPER_ADMIN, UserRole.DIRETOR]:
        dashboard_type = "admin_global"
    elif current_user.role == UserRole.DONO_ASSINANTE:
        # Buscar informações do segmento, se existir
        if current_user.subscriber and current_user.subscriber.segment_id:
            # Obter o segmento do banco de dados
            segment = db.query(Segment).filter(
                Segment.id == current_user.subscriber.segment_id,
                Segment.is_active == True
            ).first()
            
            if segment:
                # Determinar o tipo de dashboard com base no nome do segmento
                nome_segmento = segment.nome.lower() if segment.nome else ""
                
                if "veterinaria" in nome_segmento:
                    dashboard_type = "clinica_veterinaria"
                elif "odontologia" in nome_segmento or "dental" in nome_segmento:
                    dashboard_type = "clinica_odontologica"
                else:
                    dashboard_type = "clinica_padrao"
    else:
        # Para COLABORADOR_NIVEL_2 e outros papéis
        dashboard_type = "usuario_clinica"
    
    return {"dashboard_type": dashboard_type}