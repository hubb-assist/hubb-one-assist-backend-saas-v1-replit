"""
Schemas Pydantic para assinantes
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator


class SubscriberBase(BaseModel):
    """Schema base para assinantes com atributos comuns"""
    name: str = Field(..., min_length=2, max_length=100, description="Nome do responsável")
    clinic_name: str = Field(..., min_length=2, max_length=100, description="Nome da clínica")
    email: EmailStr = Field(..., description="Email de contato principal")
    phone: Optional[str] = Field(None, description="Telefone de contato")
    document: str = Field(..., description="CPF ou CNPJ")
    zip_code: Optional[str] = Field(None, description="CEP")
    address: Optional[str] = Field(None, description="Logradouro/rua")
    number: Optional[str] = Field(None, description="Número do endereço")
    city: Optional[str] = Field(None, description="Cidade")
    state: Optional[str] = Field(None, max_length=2, description="Estado (UF)")
    segment_id: UUID = Field(..., description="ID do segmento ao qual o assinante pertence")
    plan_id: Optional[UUID] = Field(None, description="ID do plano contratado")
    is_active: bool = True

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class SubscriberCreate(SubscriberBase):
    """Schema para criação de novo assinante"""
    # Campo necessário para criar o usuário administrador do assinante
    admin_password: str = Field(..., min_length=8, description="Senha do usuário administrador")

    @validator('document')
    def validate_document(cls, v):
        """Valida o formato do documento (CPF ou CNPJ)"""
        # Remove caracteres não numéricos
        nums = ''.join(filter(str.isdigit, v))
        
        # Verifica se é um CPF (11 dígitos) ou CNPJ (14 dígitos)
        if len(nums) not in (11, 14):
            raise ValueError("Documento deve ser um CPF (11 dígitos) ou CNPJ (14 dígitos)")
            
        return nums  # Retorna apenas os números


class SubscriberUpdate(BaseModel):
    """Schema para atualização de assinante - todos os campos são opcionais"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    clinic_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    document: Optional[str] = None
    zip_code: Optional[str] = None
    address: Optional[str] = None
    number: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    segment_id: Optional[UUID] = None
    plan_id: Optional[UUID] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid"  # impede campos extras
    )

    @validator('document')
    def validate_document(cls, v):
        """Valida o formato do documento (CPF ou CNPJ)"""
        if v is None:
            return v
            
        # Remove caracteres não numéricos
        nums = ''.join(filter(str.isdigit, v))
        
        # Verifica se é um CPF (11 dígitos) ou CNPJ (14 dígitos)
        if len(nums) not in (11, 14):
            raise ValueError("Documento deve ser um CPF (11 dígitos) ou CNPJ (14 dígitos)")
            
        return nums  # Retorna apenas os números


class SubscriberResponse(SubscriberBase):
    """Schema para resposta de assinante - inclui campos somente leitura"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class PaginatedSubscriberResponse(BaseModel):
    """Schema para resposta paginada de assinantes"""
    total: int
    page: int
    size: int
    items: List[SubscriberResponse]