from typing import Optional, Dict, Any
from uuid import UUID
from datetime import date
from decimal import Decimal

from app.domain.cost_fixed.entities import CostFixedEntity
from app.domain.cost_fixed.interfaces import ICostFixedRepository


class UpdateCostFixedUseCase:
    """Caso de uso para atualizar um custo fixo existente."""

    def __init__(self, repository: ICostFixedRepository):
        self.repository = repository

    def execute(
        self,
        cost_fixed_id: UUID,
        subscriber_id: UUID,
        update_data: Dict[str, Any]
    ) -> Optional[CostFixedEntity]:
        """
        Atualiza um custo fixo existente.
        
        Args:
            cost_fixed_id: ID do custo fixo a ser atualizado
            subscriber_id: ID do assinante para verificação de permissão
            update_data: Dicionário com os campos a serem atualizados
            
        Returns:
            Entidade de custo fixo atualizada se encontrada, None caso contrário
            
        Raises:
            ValueError: Se o custo fixo não for encontrado ou se houver erro de validação
        """
        # Verifica se o custo fixo existe e pertence ao assinante
        cost_fixed = self.repository.get_by_id(cost_fixed_id, subscriber_id)
        
        if not cost_fixed:
            raise ValueError(f"Custo fixo com ID {cost_fixed_id} não encontrado ou não pertence ao assinante")
        
        try:
            # Filtra apenas os campos permitidos para atualização
            allowed_fields = {'nome', 'valor', 'data', 'observacoes', 'is_active'}
            filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
            
            # Converte valor para Decimal se presente
            if 'valor' in filtered_data and filtered_data['valor'] is not None:
                filtered_data['valor'] = Decimal(str(filtered_data['valor']))
            
            # Atualiza no repositório
            updated_cost_fixed = self.repository.update(cost_fixed_id, filtered_data, subscriber_id)
            
            if not updated_cost_fixed:
                raise ValueError(f"Não foi possível atualizar o custo fixo com ID {cost_fixed_id}")
                
            return updated_cost_fixed
            
        except ValueError as e:
            # Re-lança a exceção para ser tratada pela camada de API
            raise ValueError(f"Erro ao atualizar custo fixo: {str(e)}")
        except Exception as e:
            raise ValueError(f"Erro inesperado ao atualizar custo fixo: {str(e)}")