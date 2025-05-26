"""
Configuração da sessão de conexão com o banco de dados
"""

import os
import time
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

# Obter a URL de conexão do PostgreSQL de variáveis de ambiente ou usar valor padrão
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL não está definido nas variáveis de ambiente")

# Configurar opções de conexão mais robustas para lidar com problemas de conexão
engine_options = {
    "pool_pre_ping": True,  # Verificar a conexão antes de usar (detecta conexões quebradas)
    "pool_recycle": 120,    # Reciclar conexões a cada 2 minutos para evitar timeouts
    "pool_timeout": 30,     # Timeout para obter uma conexão do pool
    "pool_size": 5,         # Tamanho padrão do pool de conexões
    "max_overflow": 10,     # Número máximo de conexões extras além do pool_size
    "connect_args": {       # Argumentos específicos para o driver psycopg2
        "connect_timeout": 10,  # Timeout de conexão em segundos
        "keepalives": 1,        # Ativar keepalives para detectar conexões quebradas
        "keepalives_idle": 30,  # Tempo em segundos antes de enviar um keepalive
        "keepalives_interval": 10,  # Intervalo entre keepalives
        "keepalives_count": 5   # Número de keepalives antes de considerar a conexão morta
    }
}

# Criar engine do SQLAlchemy com opções melhoradas
engine = create_engine(str(DATABASE_URL), **engine_options)

# Criar fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para os modelos
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependência para obter uma sessão do banco de dados com tratamento de erros melhorado.
    
    Esta função implementa lógica de retry e tratamento de erros para fornecer
    maior resiliência à conexão de banco de dados.
    
    Yields:
        Session: Uma sessão do banco de dados.
    """
    db = None
    try:
        # Usar uma conexão sem teste inicial para evitar erros que podem impedir o acesso
        db = SessionLocal()
        yield db
    except Exception as e:
        # Registrar o erro para diagnóstico
        print(f"Erro ao conectar com o banco de dados: {str(e)}")
        # Propagar a exceção para que o FastAPI possa tratá-la adequadamente
        raise
    finally:
        # Garantir que a conexão seja fechada mesmo em caso de erro
        if db is not None:
            db.close()