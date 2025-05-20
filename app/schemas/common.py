"""
Schemas comuns utilizados em toda a aplicação.
"""
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

# Tipo genérico para o conteúdo dos itens paginados
T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Resposta paginada genérica para listas de recursos.
    """
    items: List[T]
    total: int = Field(..., description="Total de itens disponíveis")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")