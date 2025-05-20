from abc import ABC, abstractmethod
from uuid import UUID
from datetime import date
from typing import List, Optional

from app.domain.cost_clinical.entities import CostClinicalEntity
from app.schemas.custo_clinico import CustoClinicalCreate, CustoClinicalUpdate

class ICostClinicalRepository(ABC):
    """
    Interface para o repositório de custos clínicos.
    """
    
    @abstractmethod
    def create(self, data: CustoClinicalCreate, subscriber_id: UUID) -> CostClinicalEntity:
        """
        Cria um novo custo clínico.
        
        Args:
            data: Dados do custo clínico a ser criado
            subscriber_id: ID do assinante
            
        Returns:
            Entidade do custo clínico criado
        """
        pass

    @abstractmethod
    def get_by_id(self, id: UUID, subscriber_id: UUID) -> Optional[CostClinicalEntity]:
        """
        Obtém um custo clínico pelo ID.
        
        Args:
            id: ID do custo clínico
            subscriber_id: ID do assinante
            
        Returns:
            Entidade do custo clínico ou None se não encontrado
        """
        pass

    @abstractmethod
    def update(self, id: UUID, data: CustoClinicalUpdate, subscriber_id: UUID) -> Optional[CostClinicalEntity]:
        """
        Atualiza um custo clínico existente.
        
        Args:
            id: ID do custo clínico a ser atualizado
            data: Dados para atualização
            subscriber_id: ID do assinante
            
        Returns:
            Entidade do custo clínico atualizada ou None se não encontrado
        """
        pass

    @abstractmethod
    def delete(self, id: UUID, subscriber_id: UUID) -> bool:
        """
        Remove logicamente um custo clínico.
        
        Args:
            id: ID do custo clínico a ser removido
            subscriber_id: ID do assinante
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        pass

    @abstractmethod
    def list_all(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[CostClinicalEntity]:
        """
        Lista todos os custos clínicos do assinante com paginação e filtragem por data.
        
        Args:
            subscriber_id: ID do assinante
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar (paginação)
            date_from: Data inicial para filtro
            date_to: Data final para filtro
            
        Returns:
            Lista de entidades de custos clínicos
        """
        pass