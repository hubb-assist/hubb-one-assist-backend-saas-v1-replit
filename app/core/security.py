"""
Funções e utilitários de segurança
"""
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import jwt
from passlib.context import CryptContext

# Configurações de segurança
SECRET_KEY = os.environ.get("SECRET_KEY", "insecure_key_for_dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 semana

# Contexto do passlib para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None, data: Dict = None
) -> str:
    """
    Cria um token JWT
    
    Args:
        subject: Subject do token (normalmente user_id)
        expires_delta: Tempo de expiração opcional
        data: Dados adicionais a serem incluídos no token
        
    Returns:
        str: Token JWT codificado
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    
    if data:
        to_encode.update(data)
        
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto puro corresponde ao hash
    
    Args:
        plain_password: Senha em texto puro
        hashed_password: Hash da senha armazenado
        
    Returns:
        bool: True se a senha corresponder ao hash, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Gera hash da senha usando bcrypt
    
    Args:
        password: Senha em texto puro
        
    Returns:
        str: Hash da senha
    """
    return pwd_context.hash(password)