"""
Caso de uso para atualização parcial de um insumo.
"""
from typing import Optional, Dict, Any
from uuid import UUID

from app.domain.insumo.interfaces import InsumoRepositoryInterface


class UpdateInsumoUseCase:
    """
    Caso de uso para atualização parcial de um insumo.
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
        insumo_id: UUID,
        subscriber_id: UUID,
        nome: Optional[str] = None,
        tipo: Optional[str] = None,
        unidade: Optional[str] = None,
        categoria: Optional[str] = None,
        quantidade: Optional[float] = None,
        observacoes: Optional[str] = None,
        modulo_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Executa o caso de uso para atualização parcial de um insumo.
        
        Args:
            insumo_id: ID do insumo a ser atualizado
            subscriber_id: ID do assinante proprietário para validação
            nome: Novo nome do insumo (opcional)
            tipo: Novo tipo do insumo (opcional)
            unidade: Nova unidade de medida (opcional)
            categoria: Nova categoria do insumo (opcional)
            quantidade: Nova quantidade disponível (opcional)
            observacoes: Novas observações adicionais (opcional)
            modulo_id: Novo ID do módulo relacionado (opcional)
            is_active: Novo status de ativação (opcional)
            
        Returns:
            Dict[str, Any]: Dados do insumo atualizado
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
        """
        # Verificar se o insumo existe
        entity = self.repository.get_by_id(insumo_id, subscriber_id)
        
        # Preparar dados para atualização
        update_data = {}
        
        if nome is not None:
            update_data["nome"] = nome
            
        if tipo is not None:
            update_data["tipo"] = tipo
            
        if unidade is not None:
            update_data["unidade"] = unidade
            
        if categoria is not None:
            update_data["categoria"] = categoria
            
        if quantidade is not None:
            update_data["quantidade"] = quantidade
            
        if observacoes is not None:
            update_data["observacoes"] = observacoes
            
        if modulo_id is not None:
            update_data["modulo_id"] = modulo_id
            
        if is_active is not None:
            update_data["is_active"] = is_active
        
        # Se não há dados para atualizar, retornar insumo atual
        if not update_data:
            return entity.to_dict()
        
        # Persistir atualização no repositório
        updated_entity = self.repository.update(insumo_id, subscriber_id, update_data)
        
        # Retornar como dicionário
        return updated_entity.to_dict()