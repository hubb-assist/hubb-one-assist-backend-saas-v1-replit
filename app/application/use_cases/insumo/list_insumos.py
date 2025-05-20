"""
Caso de uso para listar insumos com filtros opcionais.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class ListInsumosUseCase:
    """
    Caso de uso para listar insumos com filtros opcionais.
    
    Responsável por buscar insumos no repositório aplicando filtros
    e preparando os dados para apresentação.
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            repository: Implementação do repositório de insumos
        """
        self.repository = repository
    
    def execute(self, subscriber_id: UUID, filters: Optional[Dict[str, Any]] = None) -> List[InsumoEntity]:
        """
        Executa o caso de uso para listar insumos.
        
        Args:
            subscriber_id: ID do assinante para filtrar insumos
            filters: Dicionário de filtros a serem aplicados
            
        Returns:
            List[InsumoEntity]: Lista de entidades de insumo
            
        Raises:
            ValueError: Se ocorrer um erro durante a listagem
        """
        # Validar subscriber_id
        if not subscriber_id:
            raise ValueError("ID do assinante é obrigatório")
            
        # Buscar insumos no repositório
        return self.repository.list(subscriber_id=subscriber_id, filters=filters)


class ListInsumosByFilterUseCase:
    """
    Caso de uso especializado para listar insumos com filtros específicos.
    
    Permite filtragem por vários critérios e enriquece os resultados
    com dados calculados para a visualização.
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            repository: Implementação do repositório de insumos
        """
        self.repository = repository
    
    def execute(
        self, 
        subscriber_id: UUID, 
        nome: Optional[str] = None,
        categoria: Optional[str] = None,
        fornecedor: Optional[str] = None,
        estoque_baixo: Optional[bool] = None,
        module_id: Optional[UUID] = None
    ) -> List[InsumoEntity]:
        """
        Executa o caso de uso para listar insumos com filtros específicos.
        
        Args:
            subscriber_id: ID do assinante
            nome: Filtrar por nome (busca parcial)
            categoria: Filtrar por categoria (busca exata)
            fornecedor: Filtrar por fornecedor (busca parcial)
            estoque_baixo: Filtrar insumos com estoque abaixo do mínimo
            module_id: Filtrar por módulo associado
            
        Returns:
            List[InsumoEntity]: Lista de entidades de insumo filtradas
            
        Raises:
            ValueError: Se ocorrer um erro durante a listagem
        """
        # Validar subscriber_id
        if not subscriber_id:
            raise ValueError("ID do assinante é obrigatório")
            
        # Construir filtros
        filters = {}
        
        if nome:
            filters["nome"] = nome
            
        if categoria:
            filters["categoria"] = categoria
            
        if fornecedor:
            filters["fornecedor"] = fornecedor
            
        if estoque_baixo is not None:
            filters["estoque_baixo"] = estoque_baixo
            
        if module_id:
            filters["module_id"] = module_id
            
        # Buscar insumos no repositório
        insumos = self.repository.list(subscriber_id=subscriber_id, filters=filters)
        
        # Calcular propriedades adicionais para cada insumo
        for insumo in insumos:
            # Essas propriedades já estão disponíveis na entidade
            # Só precisamos verificar para calcular valores derivados se necessário
            _ = insumo.esta_abaixo_do_minimo()  # Atualiza a propriedade 
            _ = insumo.esta_expirado()  # Atualiza a propriedade
            
        return insumos