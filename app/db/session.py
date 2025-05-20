"""
Configuração da sessão do banco de dados.
"""
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator:
    """
    Fornece uma sessão de banco de dados para as rotas.
    
    Returns:
        Generator: Gerador da sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()