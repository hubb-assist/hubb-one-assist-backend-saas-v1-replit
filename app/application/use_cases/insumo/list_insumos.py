"""
Caso de uso para listar insumos com filtros e paginação.
"""
from typing import Dict, Any, Optional, List
from uuid import UUID

from app.domain.insumo.interfaces import InsumoRepositoryInterface


class ListInsumosUseCase:
    """
    Caso de uso para listar insumos com filtros e paginação.
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
        nome: Optional[str] = None,
        tipo: Optional[str] = None,
        categoria: Optional[str] = None,
        modulo_id: Optional[UUID] = None,
        is_active: Optional[bool] = True
    ) -> Dict[str, Any]:
        """
        Executa o caso de uso para listar insumos com filtros e paginação.
        
        Args:
            subscriber_id: ID do assinante proprietário
            skip: Número de registros a pular (para paginação)
            limit: Número máximo de registros a retornar
            nome: Filtro pelo nome (opcional)
            tipo: Filtro pelo tipo (opcional)
            categoria: Filtro pela categoria (opcional)
            modulo_id: Filtro pelo ID do módulo (opcional)
            is_active: Filtro pelo status de ativação (opcional)
            
        Returns:
            Dict[str, Any]: Dados dos insumos encontrados com paginação
        """
        # Preparar filtros
        filters = {}
        if nome:
            filters["nome"] = nome
        if tipo:
            filters["tipo"] = tipo
        if categoria:
            filters["categoria"] = categoria
        if modulo_id:
            filters["modulo_id"] = modulo_id
        if is_active is not None:
            filters["is_active"] = is_active
        
        # Buscar no repositório
        insumos = self.repository.list(
            subscriber_id=subscriber_id,
            skip=skip,
            limit=limit,
            filters=filters
        )
        
        # Preparar resposta
        return {
            "total": len(insumos),
            "items": [insumo.to_dict() for insumo in insumos]
        }