"""
Caso de uso para criar um novo insumo.
"""
from typing import Dict, Any
from uuid import UUID

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
        subscriber_id: UUID,
        quantidade: float = 0,
        observacoes: str = None,
        modulo_id: UUID = None
    ) -> Dict[str, Any]:
        """
        Executa o caso de uso para criar um novo insumo.
        
        Args:
            nome: Nome do insumo
            tipo: Tipo do insumo
            unidade: Unidade de medida
            categoria: Categoria do insumo
            subscriber_id: ID do assinante
            quantidade: Quantidade do insumo
            observacoes: Observações adicionais
            modulo_id: ID do módulo associado
            
        Returns:
            Dict[str, Any]: Dados do insumo criado
            
        Raises:
            ValueError: Se os dados forem inválidos
        """
        # Criar a entidade
        insumo = InsumoEntity(
            nome=nome,
            tipo=tipo,
            unidade=unidade,
            categoria=categoria,
            subscriber_id=subscriber_id,
            quantidade=quantidade,
            observacoes=observacoes,
            modulo_id=modulo_id
        )
        
        # Salvar no repositório
        created_insumo = self.repository.create(insumo)
        
        # Retornar os dados
        return created_insumo.to_dict()