"""
Configurações e utilitários de segurança.
"""
import os
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from passlib.context import CryptContext
from jose import jwt

# Configuração para geração de hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurações de JWT
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "temporarysecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(
    subject: Union[str, Any], 
    role: str = None,
    subscriber_id: str = None,
    segment_id: str = None, 
    permissions: dict = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um token JWT para autenticação.
    
    Args:
        subject: Identificador único do usuário (geralmente ID)
        role: Papel do usuário no sistema
        subscriber_id: ID do assinante ao qual o usuário pertence
        segment_id: ID do segmento ao qual o usuário pertence
        permissions: Dicionário de permissões personalizadas
        expires_delta: Tempo de expiração personalizado
        
    Returns:
        str: Token JWT codificado
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Adicionar claims adicionais ao token se fornecidos
    if role:
        to_encode["role"] = role
    if subscriber_id:
        to_encode["subscriber_id"] = str(subscriber_id)
    if segment_id:
        to_encode["segment_id"] = str(segment_id)
    if permissions:
        to_encode["permissions"] = permissions
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha fornecida corresponde ao hash armazenado.
    
    Args:
        plain_password: Senha em texto puro
        hashed_password: Hash da senha armazenado
        
    Returns:
        bool: True se a senha corresponder, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera um hash seguro para a senha.
    
    Args:
        password: Senha em texto puro
        
    Returns:
        str: Hash da senha
    """
    return pwd_context.hash(password)