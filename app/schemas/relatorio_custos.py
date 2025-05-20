"""
Esquemas Pydantic para relatórios de custos
"""
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, validator, ConfigDict


class ReportTypeEnum(str, Enum):
    """
    Tipos de relatórios disponíveis
    """
    MENSAL = "mensal"
    TRIMESTRAL = "trimestral"
    ANUAL = "anual"
    CUSTOMIZADO = "customizado"


class RelatorioCustosBase(BaseModel):
    """
    Base para esquemas de relatórios de custos
    """
    date_from: date = Field(..., description="Data inicial do período do relatório")
    date_to: date = Field(..., description="Data final do período do relatório")
    report_type: ReportTypeEnum = Field(..., description="Tipo do relatório")
    title: str = Field(..., description="Título do relatório")
    description: Optional[str] = Field(None, description="Descrição detalhada do relatório")
    
    @validator('date_to')
    def date_to_after_date_from(cls, v, values):
        """
        Valida que a data final é posterior à data inicial
        """
        if 'date_from' in values and v < values['date_from']:
            raise ValueError('A data final deve ser posterior à data inicial')
        return v


class RelatorioCustosCreate(RelatorioCustosBase):
    """
    Esquema para criação de um relatório de custos
    """
    pass


class RelatorioCustosUpdate(BaseModel):
    """
    Esquema para atualização de um relatório de custos
    Todos os campos são opcionais
    """
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    report_type: Optional[ReportTypeEnum] = None
    title: Optional[str] = None
    description: Optional[str] = None
    
    @validator('date_to')
    def date_to_after_date_from(cls, v, values):
        """
        Valida que a data final é posterior à data inicial
        """
        if v and 'date_from' in values and values['date_from'] and v < values['date_from']:
            raise ValueError('A data final deve ser posterior à data inicial')
        return v


class RelatorioCustosResponse(RelatorioCustosBase):
    """
    Esquema para resposta de um relatório de custos
    """
    id: UUID
    subscriber_id: UUID
    total_fixed_costs: Decimal
    total_variable_costs: Decimal
    total_clinical_costs: Decimal
    total_supplies_costs: Decimal
    grand_total: Decimal
    is_active: bool
    created_at: date
    updated_at: date
    
    model_config = ConfigDict(from_attributes=True)


class RelatorioCustosList(BaseModel):
    """
    Esquema para listar relatórios de custos paginados
    """
    items: List[RelatorioCustosResponse]
    total: int
    skip: int
    limit: int


class RelatorioCustosDetalhado(RelatorioCustosResponse):
    """
    Esquema para um relatório detalhado que inclui dados adicionais
    sobre os custos no período
    """
    # Detalhes de custos por categoria
    detalhes_fixos: Optional[dict] = None
    detalhes_variaveis: Optional[dict] = None
    detalhes_clinicos: Optional[dict] = None
    detalhes_insumos: Optional[dict] = None
    
    # Gráficos e análises
    distribuicao_percentual: Optional[dict] = None
    evolucao_mensal: Optional[dict] = None