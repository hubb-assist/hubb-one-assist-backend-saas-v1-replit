from pydantic import BaseModel, Field, condecimal
from uuid import UUID
from datetime import date, datetime
from typing import Optional, List

# --- PAYABLES ---
class PayableBase(BaseModel):
    description: str = Field(..., min_length=3, max_length=255)
    amount: condecimal(gt=0, decimal_places=2)
    due_date: date
    notes: Optional[str] = None

class PayableCreate(PayableBase):
    pass

class PayableUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=3, max_length=255)
    amount: Optional[condecimal(gt=0, decimal_places=2)]
    due_date: Optional[date]
    paid: Optional[bool]
    payment_date: Optional[datetime]
    notes: Optional[str]
    is_active: Optional[bool]

class PayableResponse(PayableBase):
    id: UUID
    subscriber_id: UUID
    paid: bool
    payment_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- RECEIVABLES ---
class ReceivableBase(BaseModel):
    patient_id: UUID
    description: str = Field(..., min_length=3, max_length=255)
    amount: condecimal(gt=0, decimal_places=2)
    due_date: date
    notes: Optional[str] = None

class ReceivableCreate(ReceivableBase):
    pass

class ReceivableUpdate(BaseModel):
    patient_id: Optional[UUID]
    description: Optional[str] = Field(None, min_length=3, max_length=255)
    amount: Optional[condecimal(gt=0, decimal_places=2)]
    due_date: Optional[date]
    received: Optional[bool]
    receive_date: Optional[datetime]
    notes: Optional[str]
    is_active: Optional[bool]

class ReceivableResponse(ReceivableBase):
    id: UUID
    subscriber_id: UUID
    received: bool
    receive_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- CASH FLOW & PROFIT ---
class CashFlowSummary(BaseModel):
    total_inflows: condecimal(decimal_places=2)
    total_outflows: condecimal(decimal_places=2)
    net_flow: condecimal(decimal_places=2)

class ProfitCalculation(BaseModel):
    total_revenue: condecimal(decimal_places=2)
    total_costs: condecimal(decimal_places=2)
    gross_profit: condecimal(decimal_places=2)
    net_profit: condecimal(decimal_places=2)

# --- FILTER PARAMETERS ---
class FinanceFilterParams(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    paid_status: Optional[bool] = None 
    min_amount: Optional[condecimal(decimal_places=2)] = None
    max_amount: Optional[condecimal(decimal_places=2)] = None