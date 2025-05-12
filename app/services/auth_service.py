"""
Serviço para autenticação de usuários
"""

import os
from datetime import timedelta
from typing import Optional, Dict, Any, Tuple

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.db.models import User
from app.services.user_service import UserService
from app.schemas.auth import Token, TokenData
from app.core.security import (
    create_access_token, 
    create_refresh_token, 
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)


class AuthService:
    """
    Serviço para autenticação de usuários e gerenciamento de tokens
    """
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Autentica um usuário pelo email e senha
        
        Args:
            db: Sessão do banco de dados
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            Optional[User]: Usuário autenticado ou None
        """
        user = UserService.get_user_by_email(db, email)
        
        if not user:
            return None
            
        if not UserService.verify_password(password, user.password_hash):
            return None
            
        if not user.is_active:
            return None
            
        return user
    
    @staticmethod
    def create_login_tokens(user: User) -> Token:
        """
        Cria tokens JWT para um usuário autenticado
        
        Args:
            user: Usuário autenticado
            
        Returns:
            Token: Access token e refresh token
        """
        # Obter segment_id do assinante associado ao usuário
        segment_id = None
        if user.subscriber_id and user.subscriber:
            segment_id = str(user.subscriber.segment_id) if user.subscriber.segment_id else None
        
        # Dados para incluir no token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value if user.role else None,
            "subscriber_id": str(user.subscriber_id) if user.subscriber_id else None,
            "segment_id": segment_id,
            "permissions": []  # Implementação futura de permissões granulares
        }
        
        # Criar access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        # Criar refresh token
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = create_refresh_token(
            data=token_data,
            expires_delta=refresh_token_expires
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    @staticmethod
    def refresh_access_token(refresh_token: str, db: Session) -> Token:
        """
        Cria um novo access token a partir de um refresh token válido
        
        Args:
            refresh_token: Refresh token válido
            db: Sessão do banco de dados
            
        Returns:
            Token: Novo access token e novo refresh token
            
        Raises:
            HTTPException: Se o refresh token for inválido
        """
        try:
            # Verificar se o refresh token é válido
            payload = decode_token(refresh_token)
            
            # Extrair dados do payload
            user_id = int(payload.get("sub"))
            
            # Buscar usuário no banco
            user = UserService.get_user_by_id(db, user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuário inativo ou inexistente",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Gerar novos tokens
            return AuthService.create_login_tokens(user)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    @staticmethod
    def get_token_data_from_request(request: Request) -> Optional[TokenData]:
        """
        Extrai e valida o token JWT do cookie na requisição
        
        Args:
            request: Requisição HTTP
            
        Returns:
            Optional[TokenData]: Dados do token ou None
        """
        access_token = request.cookies.get("access_token")
        
        if not access_token:
            return None
            
        try:
            # Decodificar o token
            payload = decode_token(access_token)
            
            # Extrair dados do token
            user_id = int(payload.get("sub"))
            email = payload.get("email")
            role = payload.get("role")
            subscriber_id = payload.get("subscriber_id")
            segment_id = payload.get("segment_id")
            permissions = payload.get("permissions", [])
            exp = payload.get("exp")
            
            return TokenData(
                user_id=user_id,
                email=email,
                role=role,
                subscriber_id=subscriber_id,
                segment_id=segment_id,
                permissions=permissions,
                exp=exp
            )
        except:
            return None
            
    @staticmethod
    def set_auth_cookies(response, token: Token) -> None:
        """
        Configura cookies HttpOnly com os tokens
        
        Args:
            response: Resposta HTTP para adicionar cookies
            token: Tokens JWT
        """
        # Sempre use Secure=True para todas as conexões
        # A maioria dos ambientes de desenvolvimento atual usa HTTPS
        # incluindo Replit, Netlify, Vercel, etc.
        
        # Configurar cookie de access token (curta duração)
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            secure=True,  # Sempre use Secure para HTTPS
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="none",  # Permitir cross-site em qualquer contexto
            path="/"
        )
        
        # Configurar cookie de refresh token (longa duração)
        response.set_cookie(
            key="refresh_token",
            value=token.refresh_token,
            httponly=True,
            secure=True,  # Sempre use Secure para HTTPS
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            samesite="none",  # Permitir cross-site em qualquer contexto
            path="/"
        )
        
    @staticmethod
    def clear_auth_cookies(response) -> None:
        """
        Remove os cookies de autenticação
        
        Args:
            response: Resposta HTTP para remover cookies
        """
        response.delete_cookie(
            key="access_token", 
            path="/", 
            secure=True, 
            httponly=True, 
            samesite="none"
        )
        response.delete_cookie(
            key="refresh_token", 
            path="/", 
            secure=True, 
            httponly=True, 
            samesite="none"
        )