"""
Rotas da API para autenticação de usuários
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import Token, LoginRequest, RefreshTokenRequest

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=dict)
async def login(
    response: Response,
    user_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Autentica um usuário e retorna tokens JWT
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
    
    # Resposta de sucesso
    return {"mensagem": "Login realizado com sucesso."}


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