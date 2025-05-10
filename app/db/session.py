"""
Configuração da sessão de conexão com o banco de dados
"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

# Obter a URL de conexão do PostgreSQL de variáveis de ambiente ou usar valor padrão
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL não está definido nas variáveis de ambiente")

# Criar engine do SQLAlchemy
engine = create_engine(str(DATABASE_URL))

# Criar fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para os modelos
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependência para obter uma sessão do banco de dados.
    
    Yields:
        Session: Uma sessão do banco de dados.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()