"""
Rotas públicas da API para criação de dispositivos Arduino sem autenticação
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.arduino_device_service import ArduinoDeviceService
from app.schemas.arduino_device import PublicArduinoDeviceCreate, ArduinoDeviceResponse

# Criar router para operações públicas
router = APIRouter(
    prefix="/public/arduino",
    tags=["public", "arduino"],
    responses={
        400: {"description": "Requisição inválida"},
        404: {"description": "Dispositivo não encontrado"},
        409: {"description": "Conflito - dispositivo já existe"}
    }
)


@router.post("/register", response_model=ArduinoDeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_arduino_device(
    device_data: PublicArduinoDeviceCreate,
    db: Session = Depends(get_db)
):
    """
    Registra um novo dispositivo Arduino a partir do processo de ativação pública.
    Este endpoint é acessível sem autenticação, mas protegido por CORS.
    
    Args:
        device_data: Dados do novo dispositivo
        db: Sessão do banco de dados
        
    Returns:
        dict: Mensagem de sucesso e dados do dispositivo
        
    Raises:
        HTTPException: Se houver erros de validação ou conflitos
    """
    try:
        # Preparar dados para criar o dispositivo
        device_create_data = {
            "device_id": device_data.device_id,
            "name": device_data.name,
            "description": device_data.description,
            "mac_address": device_data.mac_address,
            "firmware_version": device_data.firmware_version,
            "subscriber_code": device_data.subscriber_code
        }
        
        # Criar o dispositivo através do serviço
        device = ArduinoDeviceService.create_device_public(db, device_create_data)
        return device
        
    except ValueError as e:
        # Erro de validação (ex: MAC address inválido)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException as e:
        # Repassar exceções HTTP já formatadas pelo serviço
        raise e
    except Exception as e:
        # Erro genérico
        print(f"Erro ao registrar dispositivo Arduino: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação. Por favor, tente novamente."
        )


@router.post("/connect", status_code=status.HTTP_200_OK)
async def connect_arduino_device(
    device_id: str,
    mac_address: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Registra uma conexão de dispositivo Arduino e atualiza seu endereço IP.
    
    Args:
        device_id: ID do dispositivo
        mac_address: Endereço MAC do dispositivo
        request: Objeto de requisição FastAPI
        db: Sessão do banco de dados
        
    Returns:
        dict: Mensagem de sucesso e status
        
    Raises:
        HTTPException: Se houver erros ou o dispositivo não for encontrado
    """
    try:
        # Obter o endereço IP do dispositivo - extrai do X-Forwarded-For ou diretamente do client
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # Se há múltiplos IPs, pegamos o primeiro (mais próximo do cliente)
            client_ip = x_forwarded_for.split(",")[0].strip()
        else:
            # Caso contrário, usar o IP direto
            client_ip = request.client.host if hasattr(request, "client") and hasattr(request.client, "host") else "0.0.0.0"
        
        # Atualizar informações de conexão
        updated = ArduinoDeviceService.update_device_connection(db, device_id, client_ip)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispositivo não encontrado"
            )
        
        return {
            "message": "Conexão registrada com sucesso",
            "status": "connected",
            "ip_address": client_ip
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro ao registrar conexão do dispositivo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação. Por favor, tente novamente."
        )