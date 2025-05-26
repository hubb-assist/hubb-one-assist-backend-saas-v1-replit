"""
Caso de uso para criação de um novo assinante.
"""
from uuid import UUID, uuid4
from typing import Optional, List

from fastapi import HTTPException

from app.domain.subscriber.entities import SubscriberEntity
from app.domain.subscriber.interfaces import SubscriberRepository
from app.schemas.subscriber import SubscriberCreate


class CreateSubscriberUseCase:
    """
    Caso de uso para criar um novo assinante.
    
    Implementa a lógica de negócio para criação de assinantes,
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
        data: SubscriberCreate,
        segment_id: Optional[UUID] = None
    ) -> SubscriberEntity:
        """
        Executa o caso de uso para criar um novo assinante.
        
        Args:
            data: Dados do assinante a ser criado
            segment_id: ID do segmento de negócio (opcional)
            
        Returns:
            SubscriberEntity: A entidade de assinante criada
            
        Raises:
            HTTPException: Se houver algum erro de validação ou negócio
        """
        # Valida CNPJ (se fornecido)
        if data.cnpj:
            if self.repository.exists_with_cnpj(data.cnpj):
                raise HTTPException(
                    status_code=400,
                    detail=f"Já existe um assinante ativo com o CNPJ {data.cnpj}"
                )
        
        # Gera um novo ID para o assinante
        subscriber_id = uuid4()
        
        # Prepara arrays para módulos e planos, se fornecidos
        modules = [UUID(module_id) for module_id in data.modules] if data.modules else []
        plans = [UUID(plan_id) for plan_id in data.plans] if data.plans else []
        
        # Cria a entidade
        subscriber = SubscriberEntity(
            id=subscriber_id,
            name=data.name,
            fantasy_name=data.fantasy_name,
            cnpj=data.cnpj,
            active_until=data.active_until,
            contact_email=data.contact_email,
            contact_phone=data.contact_phone,
            logo_url=data.logo_url,
            address=data.address,
            segment_id=segment_id or (UUID(data.segment_id) if data.segment_id else None),
            modules=modules,
            plans=plans,
            is_active=True
        )
        
        # Persiste a entidade através do repositório
        created_subscriber = self.repository.create(subscriber)
        
        return created_subscriber