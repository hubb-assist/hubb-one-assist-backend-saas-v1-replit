"""
Esquemas Pydantic para validação de dados de assinantes.
"""
from datetime import datetime
from typing import Optional, List, Union
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl


class SubscriberBase(BaseModel):
    """Esquema base para assinantes."""
    name: str = Field(..., min_length=3, max_length=255, description="Nome da empresa/assinante")
    fantasy_name: Optional[str] = Field(None, max_length=255, description="Nome fantasia")
    cnpj: Optional[str] = Field(None, max_length=18, description="CNPJ do assinante (formato: XX.XXX.XXX/XXXX-XX)")
    contact_email: Optional[EmailStr] = Field(None, description="Email de contato")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Telefone de contato")
    logo_url: Optional[HttpUrl] = Field(None, description="URL para o logo da empresa")
    address: Optional[str] = Field(None, max_length=500, description="Endereço completo")
    segment_id: Optional[str] = Field(None, description="ID do segmento de negócio")
    modules: Optional[List[str]] = Field(None, description="Lista de IDs dos módulos contratados")
    plans: Optional[List[str]] = Field(None, description="Lista de IDs dos planos contratados")

    @validator('cnpj')
    def validate_cnpj(cls, v):
        """Valida o formato do CNPJ."""
        if v is None:
            return v
        
        # Remove caracteres não numéricos para validação
        numbers = ''.join(filter(str.isdigit, v))
        
        # Verifica se tem 14 dígitos
        if len(numbers) != 14:
            raise ValueError('CNPJ deve conter 14 dígitos numéricos')
        
        # Aqui poderíamos adicionar uma validação mais complexa do CNPJ
        # como verificação de dígitos verificadores, etc.
        
        return v


class SubscriberCreate(SubscriberBase):
    """Esquema para criação de assinantes."""
    active_until: Optional[datetime] = Field(None, description="Data até quando o assinante estará ativo")


class SubscriberUpdate(BaseModel):
    """Esquema para atualização de assinantes."""
    name: Optional[str] = Field(None, min_length=3, max_length=255, description="Nome da empresa/assinante")
    fantasy_name: Optional[str] = Field(None, max_length=255, description="Nome fantasia")
    cnpj: Optional[str] = Field(None, max_length=18, description="CNPJ do assinante")
    active_until: Optional[datetime] = Field(None, description="Data até quando o assinante estará ativo")
    contact_email: Optional[EmailStr] = Field(None, description="Email de contato")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Telefone de contato")
    logo_url: Optional[HttpUrl] = Field(None, description="URL para o logo da empresa")
    address: Optional[str] = Field(None, max_length=500, description="Endereço completo")
    segment_id: Optional[str] = Field(None, description="ID do segmento de negócio")
    modules: Optional[List[str]] = Field(None, description="Lista de IDs dos módulos contratados")
    plans: Optional[List[str]] = Field(None, description="Lista de IDs dos planos contratados")
    is_active: Optional[bool] = Field(None, description="Status de ativação do assinante")

    @validator('cnpj')
    def validate_cnpj(cls, v):
        """Valida o formato do CNPJ."""
        if v is None:
            return v
        
        # Remove caracteres não numéricos para validação
        numbers = ''.join(filter(str.isdigit, v))
        
        # Verifica se tem 14 dígitos
        if len(numbers) != 14:
            raise ValueError('CNPJ deve conter 14 dígitos numéricos')
        
        return v


class SubscriberInDB(SubscriberBase):
    """Esquema para assinantes armazenados no banco de dados."""
    id: UUID
    active_until: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configuração para conversão ORM."""
        from_attributes = True


class SubscriberResponse(SubscriberInDB):
    """Esquema para resposta de assinantes."""
    # Adiciona campos específicos para resposta se necessário
    pass


class PaginatedSubscriberResponse(BaseModel):
    """Esquema para resposta paginada de assinantes."""
    items: List[SubscriberResponse]
    total: int
    page: int
    size: int
    pages: int