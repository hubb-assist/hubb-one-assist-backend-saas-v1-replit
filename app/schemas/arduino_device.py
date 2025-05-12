"""
Esquemas Pydantic para dispositivos Arduino
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, validator, IPvAnyAddress


class ArduinoDeviceBase(BaseModel):
    """Esquema base para dispositivos Arduino"""
    device_id: str = Field(..., min_length=3, max_length=50, description="ID único do dispositivo")
    name: str = Field(..., min_length=3, max_length=100, description="Nome do dispositivo")
    description: Optional[str] = Field(None, max_length=255, description="Descrição do dispositivo")
    mac_address: str = Field(..., description="Endereço MAC do dispositivo")
    firmware_version: Optional[str] = Field(None, description="Versão do firmware")
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
    
    @validator('mac_address')
    def validate_mac_address(cls, v):
        """Valida o formato do endereço MAC"""
        # Remove caracteres não permitidos
        v = v.replace('-', ':').replace('.', ':').strip().upper()
        
        # Verificar o formato básico (XX:XX:XX:XX:XX:XX)
        import re
        if not re.match(r'^([0-9A-F]{2}[:]){5}([0-9A-F]{2})$', v):
            raise ValueError("Formato de MAC inválido. Use o formato XX:XX:XX:XX:XX:XX")
            
        return v


class ArduinoDeviceCreate(ArduinoDeviceBase):
    """Esquema para criação de dispositivo Arduino"""
    subscriber_id: UUID = Field(..., description="ID do assinante ao qual o dispositivo pertence")


class ArduinoDeviceUpdate(BaseModel):
    """Esquema para atualização de dispositivo Arduino - todos os campos são opcionais"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None
    firmware_version: Optional[str] = None
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid"  # impede campos extras
    )
    
    @validator('mac_address')
    def validate_mac_address(cls, v):
        """Valida o formato do endereço MAC"""
        if v is None:
            return v
            
        # Remove caracteres não permitidos
        v = v.replace('-', ':').replace('.', ':').strip().upper()
        
        # Verificar o formato básico (XX:XX:XX:XX:XX:XX)
        import re
        if not re.match(r'^([0-9A-F]{2}[:]){5}([0-9A-F]{2})$', v):
            raise ValueError("Formato de MAC inválido. Use o formato XX:XX:XX:XX:XX:XX")
            
        return v


class ArduinoDeviceResponse(ArduinoDeviceBase):
    """Esquema para resposta de dispositivo Arduino - inclui campos somente leitura"""
    id: UUID
    ip_address: Optional[str] = None
    is_active: bool
    subscriber_id: UUID
    last_connection: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class PaginatedArduinoDeviceResponse(BaseModel):
    """Esquema para resposta paginada de dispositivos Arduino"""
    total: int
    page: int
    size: int
    items: List[ArduinoDeviceResponse]


# Esquema específico para a API pública
class PublicArduinoDeviceCreate(BaseModel):
    """Esquema para criação pública de dispositivo Arduino durante registro"""
    device_id: str = Field(..., min_length=3, max_length=50, description="ID único do dispositivo")
    name: str = Field(..., min_length=3, max_length=100, description="Nome do dispositivo")
    description: Optional[str] = Field(None, max_length=255, description="Descrição do dispositivo")
    mac_address: str = Field(..., description="Endereço MAC do dispositivo")
    firmware_version: Optional[str] = Field(None, description="Versão do firmware")
    subscriber_code: str = Field(..., description="Código do assinante para associação")
    
    @validator('mac_address')
    def validate_mac_address(cls, v):
        """Valida o formato do endereço MAC"""
        # Remove caracteres não permitidos
        v = v.replace('-', ':').replace('.', ':').strip().upper()
        
        # Verificar o formato básico (XX:XX:XX:XX:XX:XX)
        import re
        if not re.match(r'^([0-9A-F]{2}[:]){5}([0-9A-F]{2})$', v):
            raise ValueError("Formato de MAC inválido. Use o formato XX:XX:XX:XX:XX:XX")
            
        return v