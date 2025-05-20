"""
Caso de uso para criar um novo insumo.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class CreateInsumoUseCase:
    """
    Caso de uso para criar um novo insumo.
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
        nome: str,
        tipo: str,
        unidade: str,
        categoria: str,
        quantidade: float,
        subscriber_id: UUID,
        observacoes: Optional[str] = None,
        modulo_id: Optional[UUID] = None,
    ) -> dict:
        """
        Executa o caso de uso para criar um novo insumo.
        
        Args:
            nome: Nome do insumo
            tipo: Tipo do insumo
            unidade: Unidade de medida
            categoria: Categoria do insumo
            quantidade: Quantidade disponível
            subscriber_id: ID do assinante proprietário
            observacoes: Observações sobre o insumo (opcional)
            modulo_id: ID do módulo relacionado (opcional)
            
        Returns:
            dict: Dados do insumo criado
            
        Raises:
            ValueError: Se os dados forem inválidos
        """
        # Validar dados básicos
        if not nome or len(nome) < 3:
            raise ValueError("Nome do insumo deve ter pelo menos 3 caracteres")
        
        if quantidade < 0:
            raise ValueError("Quantidade deve ser um valor não negativo")
        
        # Criar entidade
        entity = InsumoEntity(
            nome=nome,
            tipo=tipo,
            unidade=unidade,
            categoria=categoria,
            quantidade=quantidade,
            subscriber_id=subscriber_id,
            observacoes=observacoes,
            modulo_id=modulo_id
        )
        
        # Persistir no repositório
        result = self.repository.create(entity)
        
        # Retornar como dicionário
        return result.to_dict()