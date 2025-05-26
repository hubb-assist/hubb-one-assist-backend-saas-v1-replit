"""
Rotas da API para gerenciamento de dispositivos Arduino
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User
from app.services.arduino_device_service import ArduinoDeviceService
from app.schemas.arduino_device import ArduinoDeviceCreate, ArduinoDeviceUpdate, ArduinoDeviceResponse, PaginatedArduinoDeviceResponse
from app.core.dependencies import get_current_user, get_current_admin_or_director

# Criar router
router = APIRouter(
    prefix="/arduino-devices",
    tags=["arduino-devices"],
    responses={404: {"description": "Dispositivo não encontrado"}}
)


@router.get("/", response_model=PaginatedArduinoDeviceResponse)
async def list_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Quantos dispositivos pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de dispositivos retornados"),
    device_id: Optional[str] = Query(None, description="Filtrar por ID do dispositivo"),
    name: Optional[str] = Query(None, description="Filtrar por nome"),
    mac_address: Optional[str] = Query(None, description="Filtrar por endereço MAC"),
    subscriber_id: Optional[UUID] = Query(None, description="Filtrar por assinante"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status de ativação")
):
    """
    Listar todos os dispositivos Arduino com opções de paginação e filtros.
    """
    filter_params = {}
    if device_id:
        filter_params["device_id"] = device_id
    if name:
        filter_params["name"] = name
    if mac_address:
        filter_params["mac_address"] = mac_address
    if subscriber_id:
        filter_params["subscriber_id"] = subscriber_id
    if is_active is not None:
        filter_params["is_active"] = is_active
        
    return ArduinoDeviceService.get_devices(db, skip, limit, filter_params, current_user=current_user)


@router.get("/{device_id}", response_model=ArduinoDeviceResponse)
async def get_device(
    device_id: UUID = Path(..., description="ID do dispositivo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obter um dispositivo Arduino pelo ID.
    """
    device = ArduinoDeviceService.get_device_by_id(db, device_id, current_user=current_user)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado"
        )
    
    return device


@router.post("/", response_model=ArduinoDeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: ArduinoDeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Criar um novo dispositivo Arduino.
    """
    return ArduinoDeviceService.create_device(db, device_data)


@router.put("/{device_id}", response_model=ArduinoDeviceResponse)
async def update_device(
    device_data: ArduinoDeviceUpdate,
    device_id: UUID = Path(..., description="ID do dispositivo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualizar um dispositivo Arduino existente.
    """
    updated_device = ArduinoDeviceService.update_device(db, device_id, device_data, current_user=current_user)
    if not updated_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado"
        )
    
    return updated_device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: UUID = Path(..., description="ID do dispositivo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Excluir um dispositivo Arduino.
    """
    success = ArduinoDeviceService.delete_device(db, device_id, current_user=current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado"
        )
    return None


@router.patch("/{device_id}/activate", response_model=ArduinoDeviceResponse)
async def activate_device(
    device_id: UUID = Path(..., description="ID do dispositivo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ativar um dispositivo Arduino.
    """
    updated_device = ArduinoDeviceService.toggle_device_status(db, device_id, activate=True, current_user=current_user)
    if not updated_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado"
        )
    
    return updated_device


@router.patch("/{device_id}/deactivate", response_model=ArduinoDeviceResponse)
async def deactivate_device(
    device_id: UUID = Path(..., description="ID do dispositivo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Desativar um dispositivo Arduino.
    """
    updated_device = ArduinoDeviceService.toggle_device_status(db, device_id, activate=False, current_user=current_user)
    if not updated_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado"
        )
    
    return updated_device