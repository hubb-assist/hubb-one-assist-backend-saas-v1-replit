"""
Caso de uso para listar insumos com filtros opcionais.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class ListInsumosUseCase:
    """
    Caso de uso para listar insumos com filtros opcionais.
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso.
        
        Args:
            repository: Repositório de insumos
        """
        self.repository = repository
    
    def execute(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        categoria: Optional[str] = None,
        tipo: Optional[str] = None,
        modulo_id: Optional[UUID] = None,
        is_active: bool = True
    ) -> Dict[str, Any]:
        """
        Executa o caso de uso para listar insumos com filtros opcionais.
        
        Args:
            subscriber_id: ID do assinante proprietário
            skip: Quantidade de registros para pular (para paginação)
            limit: Limite de registros retornados (para paginação)
            categoria: Filtro opcional por categoria
            tipo: Filtro opcional por tipo
            modulo_id: Filtro opcional por módulo
            is_active: Filtro por status de ativação (padrão: True)
            
        Returns:
            Dict[str, Any]: Dicionário com a lista de insumos e metadados
        """
        # Validar parâmetros
        if skip < 0:
            raise ValueError("O parâmetro 'skip' não pode ser negativo")
        
        if limit < 1:
            raise ValueError("O parâmetro 'limit' deve ser maior que zero")
        
        # Buscar insumos no repositório
        insumos = self.repository.list_by_subscriber(
            subscriber_id=subscriber_id,
            skip=skip,
            limit=limit,
            categoria=categoria,
            tipo=tipo,
            modulo_id=modulo_id,
            is_active=is_active
        )
        
        # Converter entidades para dicionários
        insumos_dict = [insumo.to_dict() for insumo in insumos]
        
        # Construir resposta com metadados
        return {
            "items": insumos_dict,
            "total": len(insumos_dict),
            "skip": skip,
            "limit": limit,
            "filters": {
                "categoria": categoria,
                "tipo": tipo,
                "modulo_id": str(modulo_id) if modulo_id else None,
                "is_active": is_active
            }
        }