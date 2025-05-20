"""
Sessão do SQLAlchemy para conexão com o banco de dados.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Obter URL do banco de dados da variável de ambiente
DATABASE_URL = os.environ.get("DATABASE_URL")

# Criar engine do SQLAlchemy
engine = create_engine(DATABASE_URL) if DATABASE_URL else None

# Criar classe de sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar classe base para os modelos
Base = declarative_base()


def get_db():
    """
    Retorna uma sessão de banco de dados.
    
    Yields:
        Session: Sessão de banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()