"""
Caso de uso para obter o histórico de movimentações de estoque de insumos.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID

from app.domain.insumo.interfaces import InsumoRepositoryInterface


class GetMovimentacoesUseCase:
    """
    Caso de uso para obter o histórico de movimentações de estoque de insumos.
    
    Implementa a consulta de movimentações com filtros e paginação.
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
        insumo_id: Optional[UUID] = None,
        tipo_movimento: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Executa o caso de uso para obter movimentações de estoque.
        
        Args:
            subscriber_id: ID do assinante (isolamento multitenant)
            insumo_id: Filtrar por ID do insumo específico (opcional)
            tipo_movimento: Filtrar por tipo de movimento ('entrada' ou 'saida') (opcional)
            data_inicio: Filtrar por data inicial (opcional)
            data_fim: Filtrar por data final (opcional)
            skip: Quantos registros pular (paginação)
            limit: Limite de registros a retornar (paginação)
            
        Returns:
            Tuple[List[Dict[str, Any]], int]: Lista de movimentações e contagem total
            
        Raises:
            ValueError: Se ocorrer um erro na consulta
        """
        try:
            # Validações básicas
            if tipo_movimento and tipo_movimento not in ['entrada', 'saida']:
                raise ValueError("Tipo de movimento deve ser 'entrada' ou 'saida'")
                
            if data_inicio and data_fim and data_inicio > data_fim:
                raise ValueError("Data inicial deve ser anterior à data final")
                
            # Executar consulta via repositório
            return self.repository.get_movimentacoes(
                subscriber_id=subscriber_id,
                insumo_id=insumo_id,
                tipo_movimento=tipo_movimento,
                data_inicio=data_inicio,
                data_fim=data_fim,
                skip=skip,
                limit=limit
            )
            
        except ValueError as e:
            # Propagar erros de validação
            raise ValueError(str(e))
        except Exception as e:
            # Capturar outros erros
            raise ValueError(f"Erro ao consultar histórico de movimentações: {str(e)}")