"""
Utilitários de segurança.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import os
import jwt

# Configurações de segurança
SECRET_KEY = os.environ.get("API_SECRET_KEY", "development_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 para autenticação
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    auto_error=True
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto puro corresponde ao hash.
    
    Args:
        plain_password: Senha em texto puro
        hashed_password: Hash da senha armazenado
        
    Returns:
        bool: True se a senha corresponder ao hash, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera o hash da senha.
    
    Args:
        password: Senha em texto puro
        
    Returns:
        str: Hash da senha
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um token JWT de acesso.
    
    Args:
        data: Dados a serem codificados no token
        expires_delta: Tempo de expiração do token
        
    Returns:
        str: Token JWT codificado
    """
    to_encode = data.copy()
    
    # Definir expiração
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Adicionar expiração aos dados
    to_encode.update({"exp": expire})
    
    # Criar token JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um token JWT de refresh.
    
    Args:
        data: Dados a serem codificados no token
        expires_delta: Tempo de expiração do token
        
    Returns:
        str: Token JWT de refresh codificado
    """
    to_encode = data.copy()
    
    # Definir expiração (tokens de refresh tipicamente duram mais)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Refresh token with longer lifetime (7 days)
        expire = datetime.utcnow() + timedelta(days=7)
    
    # Adicionar expiração e tipo aos dados
    to_encode.update({"exp": expire, "token_type": "refresh"})
    
    # Criar token JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt