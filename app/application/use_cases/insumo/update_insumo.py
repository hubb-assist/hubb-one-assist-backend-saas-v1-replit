"""
Caso de uso para atualizar um insumo existente.
"""
from typing import Dict, Any, Optional
from uuid import UUID

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
        modulo_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
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
            modulo_id: Novo ID de módulo (opcional)
            
        Returns:
            Dict[str, Any]: Dados do insumo atualizado
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
            ValueError: Se os dados forem inválidos
        """
        # Obter o insumo atual
        insumo = self.repository.get_by_id(insumo_id, subscriber_id)
        
        # Atualizar as informações
        insumo.update_info(
            nome=nome,
            tipo=tipo,
            unidade=unidade,
            categoria=categoria,
            quantidade=quantidade,
            observacoes=observacoes,
            modulo_id=modulo_id
        )
        
        # Salvar no repositório
        updated_insumo = self.repository.update(insumo)
        
        # Retornar os dados
        return updated_insumo.to_dict()