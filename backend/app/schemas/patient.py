"""
Schemas do Pydantic para o módulo de pacientes
"""
from datetime import date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class PatientBase(BaseModel):
    """
    Modelo base para informações de pacientes
    """
    name: str = Field(..., description="Nome completo do paciente")
    cpf: str = Field(..., description="CPF do paciente")
    rg: Optional[str] = Field(None, description="RG do paciente")
    birth_date: date = Field(..., description="Data de nascimento do paciente")
    phone: Optional[str] = Field(None, description="Telefone de contato do paciente")
    
    # Campos de endereço
    zip_code: Optional[str] = Field(None, description="CEP")
    address: Optional[str] = Field(None, description="Logradouro")
    number: Optional[str] = Field(None, description="Número")
    complement: Optional[str] = Field(None, description="Complemento")
    district: Optional[str] = Field(None, description="Bairro")
    city: Optional[str] = Field(None, description="Cidade")
    state: Optional[str] = Field(None, description="Estado (UF)")


class PatientCreate(PatientBase):
    """
    Schema usado para criar um novo paciente
    """
    pass


class PatientUpdate(BaseModel):
    """
    Schema usado para atualizar um paciente existente
    Todos os campos são opcionais para permitir atualização parcial
    """
    name: Optional[str] = Field(None, description="Nome completo do paciente")
    cpf: Optional[str] = Field(None, description="CPF do paciente")
    rg: Optional[str] = Field(None, description="RG do paciente")
    birth_date: Optional[date] = Field(None, description="Data de nascimento do paciente")
    phone: Optional[str] = Field(None, description="Telefone de contato do paciente")
    
    # Campos de endereço
    zip_code: Optional[str] = Field(None, description="CEP")
    address: Optional[str] = Field(None, description="Logradouro")
    number: Optional[str] = Field(None, description="Número")
    complement: Optional[str] = Field(None, description="Complemento")
    district: Optional[str] = Field(None, description="Bairro")
    city: Optional[str] = Field(None, description="Cidade")
    state: Optional[str] = Field(None, description="Estado (UF)")
    is_active: Optional[bool] = Field(None, description="Status de ativação do paciente")


class PatientInDB(PatientBase):
    """
    Schema que inclui campos somente disponíveis do banco de dados
    """
    id: UUID
    subscriber_id: UUID
    is_active: bool = True
    created_at: date
    updated_at: date

    class Config:
        orm_mode = True


class PatientResponse(PatientBase):
    """
    Schema para resposta da API com as informações do paciente
    """
    id: UUID
    is_active: bool = True

    class Config:
        orm_mode = True


class PatientListResponse(BaseModel):
    """
    Schema para listar múltiplos pacientes com paginação
    """
    items: List[PatientResponse]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        orm_mode = True