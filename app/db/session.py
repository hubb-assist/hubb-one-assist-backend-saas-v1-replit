"""
Configuração e inicialização da sessão do banco de dados SQLAlchemy.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuração da sessão
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Função para obter uma sessão de banco de dados
def get_db():
    """
    Dependência para obter uma sessão de banco de dados.
    A sessão é fechada automaticamente quando a requisição é concluída.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()