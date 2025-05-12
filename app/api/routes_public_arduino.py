"""
Rotas públicas da API para criação de dispositivos Arduino sem autenticação
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.arduino_device import PublicArduinoDeviceCreate
from app.services.arduino_device_service import ArduinoDeviceService

# Definir o router
router = APIRouter(
    prefix="/public/arduino",
    tags=["public"],
    responses={
        400: {"description": "Requisição inválida"},
        409: {"description": "Conflito - ID do dispositivo ou MAC já cadastrado"},
        404: {"description": "Recurso não encontrado"},
        500: {"description": "Erro interno do servidor"}
    },
)


@router.post("/", status_code=status.HTTP_201_CREATED)
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
        # Converter para o formato interno
        internal_device_data = {
            "device_id": device_data.device_id,
            "name": device_data.name,
            "description": device_data.description,
            "mac_address": device_data.mac_address,
            "firmware_version": device_data.firmware_version,
            "subscriber_code": device_data.subscriber_code
        }
        
        # Utilizar o serviço para criar o dispositivo
        new_device = ArduinoDeviceService.create_device_public(db, internal_device_data)
        
        # Retornar resposta de sucesso
        return {
            "message": "Dispositivo Arduino registrado com sucesso",
            "device": {
                "id": str(new_device.id),
                "device_id": new_device.device_id,
                "name": new_device.name,
                "subscriber_id": str(new_device.subscriber_id)
            }
        }
        
    except HTTPException as he:
        # Repassar exceções HTTP geradas pelo serviço
        raise he
    except Exception as e:
        # Log do erro e resposta genérica para outros erros
        print(f"[ERROR] Erro ao registrar dispositivo Arduino: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação. Por favor, tente novamente."
        )


@router.post("/connect", status_code=status.HTTP_200_OK)
async def connect_arduino_device(
    device_id: str,
    mac_address: str,
    db: Session = Depends(get_db)
):
    """
    Registra uma conexão de dispositivo Arduino e atualiza seu endereço IP.
    
    Args:
        device_id: ID do dispositivo
        mac_address: Endereço MAC do dispositivo
        db: Sessão do banco de dados
        
    Returns:
        dict: Mensagem de sucesso e status
        
    Raises:
        HTTPException: Se houver erros ou o dispositivo não for encontrado
    """
    try:
        # Obter o endereço IP do dispositivo
        from fastapi import Request
        request = Request
        client_ip = request.client.host
        
        # Atualizar informações de conexão
        updated = ArduinoDeviceService.update_device_connection(db, device_id, client_ip)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispositivo não encontrado"
            )
        
        # Retornar resposta de sucesso
        return {
            "message": "Conexão registrada com sucesso",
            "status": "connected",
            "ip_address": client_ip
        }
        
    except HTTPException as he:
        # Repassar exceções HTTP geradas pelo serviço
        raise he
    except Exception as e:
        # Log do erro e resposta genérica para outros erros
        print(f"[ERROR] Erro ao registrar conexão de dispositivo Arduino: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação. Por favor, tente novamente."
        )