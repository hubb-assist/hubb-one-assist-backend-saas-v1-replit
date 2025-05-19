"""
Entidades do domínio de assinantes (subscribers).

Este módulo define as entidades principais relacionadas aos assinantes
no sistema HUBB ONE Assist.
"""
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class SubscriberEntity:
    """
    Entidade Subscriber representa um assinante no sistema HUBB ONE Assist.
    
    Um assinante é uma organização ou empresa que contratou o serviço
    e tem usuários, pacientes e outros recursos associados.
    """
    
    def __init__(
        self,
        id: UUID,
        name: str,
        fantasy_name: Optional[str] = None,
        cnpj: Optional[str] = None,
        active_until: Optional[datetime] = None,
        contact_email: Optional[str] = None,
        contact_phone: Optional[str] = None,
        logo_url: Optional[str] = None,
        address: Optional[str] = None,
        segment_id: Optional[UUID] = None,
        modules: List[UUID] = None,
        plans: List[UUID] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Inicializa uma entidade Subscriber.
        
        Args:
            id: ID único do assinante
            name: Nome empresarial/razão social
            fantasy_name: Nome fantasia (opcional)
            cnpj: CNPJ da empresa (opcional)
            active_until: Data de validade da assinatura (opcional)
            contact_email: Email de contato (opcional)
            contact_phone: Telefone de contato (opcional)
            logo_url: URL para o logo da empresa (opcional)
            address: Endereço completo (opcional)
            segment_id: ID do segmento de negócio (opcional)
            modules: Lista de IDs dos módulos contratados (opcional)
            plans: Lista de IDs dos planos contratados (opcional)
            is_active: Status de ativação do assinante
            created_at: Data de criação
            updated_at: Data da última atualização
        """
        self.id = id
        self.name = name
        self.fantasy_name = fantasy_name
        self.cnpj = cnpj
        self.active_until = active_until
        self.contact_email = contact_email
        self.contact_phone = contact_phone
        self.logo_url = logo_url
        self.address = address
        self.segment_id = segment_id
        self.modules = modules or []
        self.plans = plans or []
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def update_modules(self, module_ids: List[UUID]) -> None:
        """
        Atualiza a lista de módulos do assinante.
        
        Args:
            module_ids: Lista de IDs dos módulos
        """
        self.modules = module_ids
        self.updated_at = datetime.utcnow()
    
    def update_plans(self, plan_ids: List[UUID]) -> None:
        """
        Atualiza a lista de planos do assinante.
        
        Args:
            plan_ids: Lista de IDs dos planos
        """
        self.plans = plan_ids
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Ativa o assinante."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Desativa o assinante."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def extend_subscription(self, days: int) -> None:
        """
        Estende a assinatura por um número de dias.
        
        Args:
            days: Número de dias a estender
        """
        if not self.active_until:
            self.active_until = datetime.utcnow()
        
        from datetime import timedelta
        self.active_until = self.active_until + timedelta(days=days)
        self.updated_at = datetime.utcnow()
    
    def is_subscription_active(self) -> bool:
        """
        Verifica se a assinatura está ativa.
        
        Returns:
            bool: True se a assinatura estiver ativa, False caso contrário
        """
        if not self.is_active:
            return False
        
        if not self.active_until:
            return True  # Sem data de validade = assinatura perpétua
        
        return self.active_until > datetime.utcnow()
    
    def has_module(self, module_id: UUID) -> bool:
        """
        Verifica se o assinante possui um módulo específico.
        
        Args:
            module_id: ID do módulo a verificar
            
        Returns:
            bool: True se o assinante tiver o módulo, False caso contrário
        """
        return str(module_id) in [str(m) for m in self.modules]
    
    def has_plan(self, plan_id: UUID) -> bool:
        """
        Verifica se o assinante possui um plano específico.
        
        Args:
            plan_id: ID do plano a verificar
            
        Returns:
            bool: True se o assinante tiver o plano, False caso contrário
        """
        return str(plan_id) in [str(p) for p in self.plans]