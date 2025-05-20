"""
Classe base para modelos SQLAlchemy.
"""
from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    Classe base para modelos SQLAlchemy.
    """
    id: Any
    __name__: str
    
    # Gera o nome da tabela automaticamente a partir do nome da classe
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()