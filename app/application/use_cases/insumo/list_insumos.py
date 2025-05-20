"""
Caso de uso para listar insumos com paginação e filtros.
"""

from typing import Dict, Any, Optional, List
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class ListInsumosUseCase:
    """
    Caso de uso para listar insumos com paginação e filtros.
    
    Responsável por buscar insumos com suporte a filtros
    e retornar resultados paginados para apresentação em interfaces.
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
        skip: int = 0,
        limit: int = 100,
        nome: Optional[str] = None,
        categoria: Optional[str] = None,
        fornecedor: Optional[str] = None,
        estoque_baixo: Optional[bool] = None,
        module_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Executa o caso de uso para listar insumos com filtros.
        
        Args:
            subscriber_id: ID do assinante proprietário
            skip: Quantos registros pular (para paginação)
            limit: Limite de registros por página
            nome: Filtro por nome (busca parcial)
            categoria: Filtro por categoria (busca exata)
            fornecedor: Filtro por fornecedor (busca parcial)
            estoque_baixo: Se True, lista apenas insumos com estoque abaixo do mínimo
            module_id: Filtro por módulo associado
            
        Returns:
            Dict[str, Any]: Dicionário com itens e informações de paginação
            
        Raises:
            ValueError: Se ocorrer um erro durante a busca
        """
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
        
        # Buscar no repositório com filtros
        result = self.repository.list_by_subscriber(
            subscriber_id=subscriber_id,
            skip=skip,
            limit=limit,
            filters=filters
        )
        
        # Processar entidades para o formato de apresentação
        processed_items = []
        for entity in result["items"]:
            processed_items.append(self._process_entity(entity))
        
        # Retornar resultado processado
        return {
            "items": processed_items,
            "total": result["total"],
            "page": result["page"],
            "pages": result["pages"],
            "size": result["size"]
        }
    
    def _process_entity(self, entity: InsumoEntity) -> Dict[str, Any]:
        """
        Processa uma entidade para o formato de apresentação.
        
        Args:
            entity: Entidade de insumo
            
        Returns:
            Dict[str, Any]: Dicionário com dados formatados para apresentação
        """
        # Converter associações de módulos
        modules = []
        for module in entity.modules_used:
            modules.append({
                "module_id": str(module.module_id),
                "module_nome": module.module_nome or "Módulo sem nome",
                "quantidade_padrao": module.quantidade_padrao,
                "observacao": module.observacao
            })
        
        # Retornar dicionário com dados formatados
        return {
            "id": str(entity.id),
            "nome": entity.nome,
            "descricao": entity.descricao,
            "categoria": entity.categoria,
            "valor_unitario": entity.valor_unitario,
            "unidade_medida": entity.unidade_medida,
            "estoque_minimo": entity.estoque_minimo,
            "estoque_atual": entity.estoque_atual,
            "estoque_baixo": entity.verificar_estoque_baixo(),
            "valor_total": entity.calcular_valor_total(),
            "fornecedor": entity.fornecedor,
            "codigo_referencia": entity.codigo_referencia,
            "data_validade": entity.data_validade,
            "data_compra": entity.data_compra,
            "observacoes": entity.observacoes,
            "is_active": entity.is_active,
            "created_at": entity.created_at.isoformat() if entity.created_at else None,
            "updated_at": entity.updated_at.isoformat() if entity.updated_at else None,
            "modules_used": modules
        }