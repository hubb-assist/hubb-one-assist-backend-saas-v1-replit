from uuid import UUID
from datetime import date
from decimal import Decimal
from typing import Optional

from app.domain.cost_fixed.entities import CostFixedEntity
from app.domain.cost_fixed.interfaces import ICostFixedRepository


class CreateCostFixedUseCase:
    """Caso de uso para criar um novo custo fixo."""

    def __init__(self, repository: ICostFixedRepository):
        self.repository = repository

    def execute(
        self,
        nome: str,
        valor: Decimal,
        data: date,
        subscriber_id: UUID,
        observacoes: Optional[str] = None
    ) -> CostFixedEntity:
        """
        Cria um novo custo fixo.
        
        Args:
            nome: Nome do custo fixo
            valor: Valor do custo fixo
            data: Data do custo fixo
            subscriber_id: ID do assinante
            observacoes: Observações opcionais
            
        Returns:
            Entidade de custo fixo criada
            
        Raises:
            ValueError: Se houver erro de validação
        """
        try:
            cost_fixed = CostFixedEntity(
                nome=nome,
                valor=valor,
                data=data,
                subscriber_id=subscriber_id,
                observacoes=observacoes
            )
            
            return self.repository.create(cost_fixed)
        except ValueError as e:
            # Re-lança a exceção para ser tratada pela camada de API
            raise ValueError(f"Erro ao criar custo fixo: {str(e)}")
        except Exception as e:
            raise ValueError(f"Erro inesperado ao criar custo fixo: {str(e)}")