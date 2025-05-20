"""
Caso de uso para atualizar um insumo existente.
"""
from typing import Optional
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class UpdateInsumoUseCase:
    """
    Caso de uso para atualizar um insumo existente.
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
    ) -> dict:
        """
        Executa o caso de uso para atualizar um insumo existente.
        
        Args:
            insumo_id: ID do insumo a ser atualizado
            subscriber_id: ID do assinante proprietário
            nome: Novo nome (opcional)
            tipo: Novo tipo (opcional)
            unidade: Nova unidade de medida (opcional)
            categoria: Nova categoria (opcional)
            quantidade: Nova quantidade (opcional)
            observacoes: Novas observações (opcional)
            modulo_id: Novo ID do módulo relacionado (opcional)
            is_active: Novo status de ativação (opcional)
            
        Returns:
            dict: Dados do insumo atualizado
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
            ValueError: Se os dados forem inválidos
        """
        # Validar dados básicos
        if quantidade is not None and quantidade < 0:
            raise ValueError("Quantidade deve ser um valor não negativo")
        
        # Buscar entidade atual
        entity = self.repository.get_by_id(insumo_id, subscriber_id)
        
        # Atualizar campos fornecidos
        if nome is not None:
            entity.nome = nome
        if tipo is not None:
            entity.tipo = tipo
        if unidade is not None:
            entity.unidade = unidade
        if categoria is not None:
            entity.categoria = categoria
        if quantidade is not None:
            entity.quantidade = quantidade
        if observacoes is not None:
            entity.observacoes = observacoes
        if modulo_id is not None:
            entity.modulo_id = modulo_id
        if is_active is not None:
            entity.is_active = is_active
        
        # Persistir no repositório
        result = self.repository.update(entity)
        
        # Retornar como dicionário
        return result.to_dict()