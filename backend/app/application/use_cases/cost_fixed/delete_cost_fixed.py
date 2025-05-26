from uuid import UUID

from app.domain.cost_fixed.interfaces import ICostFixedRepository


class DeleteCostFixedUseCase:
    """Caso de uso para excluir (desativar) um custo fixo."""

    def __init__(self, repository: ICostFixedRepository):
        self.repository = repository

    def execute(self, cost_fixed_id: UUID, subscriber_id: UUID) -> bool:
        """
        Exclui (desativa) um custo fixo.
        
        Args:
            cost_fixed_id: ID do custo fixo a ser excluído
            subscriber_id: ID do assinante para verificação de permissão
            
        Returns:
            True se o custo fixo foi excluído com sucesso, False caso contrário
            
        Raises:
            ValueError: Se o custo fixo não for encontrado ou não pertencer ao assinante
        """
        # Verifica se o custo fixo existe e pertence ao assinante
        cost_fixed = self.repository.get_by_id(cost_fixed_id, subscriber_id)
        
        if not cost_fixed:
            raise ValueError(f"Custo fixo com ID {cost_fixed_id} não encontrado ou não pertence ao assinante")
        
        # Executa a exclusão lógica (desativação)
        result = self.repository.delete(cost_fixed_id, subscriber_id)
        
        if not result:
            raise ValueError(f"Não foi possível excluir o custo fixo com ID {cost_fixed_id}")
            
        return result