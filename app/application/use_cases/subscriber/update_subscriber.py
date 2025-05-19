"""
Caso de uso para atualização de um assinante existente.
"""
from uuid import UUID
from typing import Optional, List
from datetime import datetime

from fastapi import HTTPException

from app.domain.subscriber.interfaces import SubscriberRepository
from app.domain.subscriber.entities import SubscriberEntity
from app.schemas.subscriber import SubscriberUpdate


class UpdateSubscriberUseCase:
    """
    Caso de uso para atualizar um assinante existente.
    
    Implementa a lógica de negócio para atualização de assinantes,
    incluindo validações e regras específicas do domínio.
    """
    
    def __init__(self, subscriber_repository: SubscriberRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            subscriber_repository: Uma implementação de SubscriberRepository
        """
        self.repository = subscriber_repository
    
    def execute(
        self,
        subscriber_id: UUID,
        data: SubscriberUpdate
    ) -> SubscriberEntity:
        """
        Executa o caso de uso para atualizar um assinante existente.
        
        Args:
            subscriber_id: ID do assinante a ser atualizado
            data: Dados atualizados do assinante
            
        Returns:
            SubscriberEntity: A entidade de assinante atualizada
            
        Raises:
            HTTPException: Se houver algum erro de validação ou negócio
        """
        # Busca o assinante no repositório
        subscriber = self.repository.get_by_id(subscriber_id)
        
        if not subscriber:
            raise HTTPException(
                status_code=404,
                detail=f"Assinante com ID {subscriber_id} não encontrado"
            )
        
        # Valida CNPJ (se fornecido e alterado)
        if data.cnpj and data.cnpj != subscriber.cnpj:
            if self.repository.exists_with_cnpj(data.cnpj, exclude_id=subscriber_id):
                raise HTTPException(
                    status_code=400,
                    detail=f"Já existe um assinante ativo com o CNPJ {data.cnpj}"
                )
        
        # Atualiza os campos se fornecidos
        if data.name is not None:
            subscriber.name = data.name
        
        if data.fantasy_name is not None:
            subscriber.fantasy_name = data.fantasy_name
        
        if data.cnpj is not None:
            subscriber.cnpj = data.cnpj
        
        if data.active_until is not None:
            subscriber.active_until = data.active_until
        
        if data.contact_email is not None:
            subscriber.contact_email = data.contact_email
        
        if data.contact_phone is not None:
            subscriber.contact_phone = data.contact_phone
        
        if data.logo_url is not None:
            subscriber.logo_url = str(data.logo_url)
        
        if data.address is not None:
            subscriber.address = data.address
        
        if data.segment_id is not None:
            subscriber.segment_id = UUID(data.segment_id)
        
        if data.modules is not None:
            subscriber.modules = [UUID(module_id) for module_id in data.modules]
        
        if data.plans is not None:
            subscriber.plans = [UUID(plan_id) for plan_id in data.plans]
        
        if data.is_active is not None:
            subscriber.is_active = data.is_active
        
        # Atualiza o timestamp de atualização
        subscriber.updated_at = datetime.utcnow()
        
        # Persiste as alterações através do repositório
        updated_subscriber = self.repository.update(subscriber)
        
        return updated_subscriber