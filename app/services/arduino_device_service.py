"""
Serviço para operações CRUD de dispositivos Arduino
"""

import uuid
from typing import Optional, Dict, Any, List, TYPE_CHECKING, Union
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from app.db.models import ArduinoDevice, Subscriber, User, UserRole
from app.schemas.arduino_device import ArduinoDeviceCreate, ArduinoDeviceUpdate, PaginatedArduinoDeviceResponse
from app.core.dependencies import apply_subscriber_filter

if TYPE_CHECKING:
    from app.db.models import User


class ArduinoDeviceService:
    """
    Serviço para operações relacionadas a dispositivos Arduino
    Implementa as regras de negócio e acesso a dados
    """
    
    @staticmethod
    def get_devices(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filter_params: Optional[Dict[str, Any]] = None,
        current_user: Optional["User"] = None
    ) -> PaginatedArduinoDeviceResponse:
        """
        Retorna uma lista paginada de dispositivos Arduino com opção de filtros
        
        Args:
            db: Sessão do banco de dados
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar (paginação)
            filter_params: Parâmetros para filtragem (opcional)
            current_user: Usuário autenticado (para aplicar filtro por subscriber_id)
            
        Returns:
            PaginatedArduinoDeviceResponse: Lista paginada de dispositivos
        """
        query = db.query(ArduinoDevice)
        total_query = db.query(ArduinoDevice)
        
        # Aplicar filtros baseados no usuário logado
        if current_user:
            query = apply_subscriber_filter(query, current_user, ArduinoDevice)
            total_query = apply_subscriber_filter(total_query, current_user, ArduinoDevice)
        
        # Aplicar filtros adicionais
        if filter_params:
            if "device_id" in filter_params:
                query = query.filter(ArduinoDevice.device_id.ilike(f"%{filter_params['device_id']}%"))
                total_query = total_query.filter(ArduinoDevice.device_id.ilike(f"%{filter_params['device_id']}%"))
                
            if "name" in filter_params:
                query = query.filter(ArduinoDevice.name.ilike(f"%{filter_params['name']}%"))
                total_query = total_query.filter(ArduinoDevice.name.ilike(f"%{filter_params['name']}%"))
                
            if "mac_address" in filter_params:
                query = query.filter(ArduinoDevice.mac_address.ilike(f"%{filter_params['mac_address']}%"))
                total_query = total_query.filter(ArduinoDevice.mac_address.ilike(f"%{filter_params['mac_address']}%"))
                
            if "subscriber_id" in filter_params:
                query = query.filter(ArduinoDevice.subscriber_id == filter_params['subscriber_id'])
                total_query = total_query.filter(ArduinoDevice.subscriber_id == filter_params['subscriber_id'])
                
            if "is_active" in filter_params:
                query = query.filter(ArduinoDevice.is_active == filter_params['is_active'])
                total_query = total_query.filter(ArduinoDevice.is_active == filter_params['is_active'])
        
        # Contagem total
        total = total_query.count()
        
        # Consulta paginada
        query = query.order_by(ArduinoDevice.name)
        query = query.offset(skip).limit(limit)
        devices = query.all()
        
        # Construir resposta paginada
        return PaginatedArduinoDeviceResponse(
            total=total,
            page=skip // limit + 1 if limit else 1,
            size=limit,
            items=devices
        )
    
    @staticmethod
    def get_device_by_id(db: Session, device_id: uuid.UUID, current_user: Optional["User"] = None) -> Optional[ArduinoDevice]:
        """
        Busca um dispositivo Arduino pelo ID
        
        Args:
            db: Sessão do banco de dados
            device_id: ID do dispositivo
            current_user: Usuário autenticado (para aplicar filtro por subscriber_id)
            
        Returns:
            Optional[ArduinoDevice]: Dispositivo encontrado ou None
        """
        query = db.query(ArduinoDevice).filter(ArduinoDevice.id == device_id)
        
        # Aplicar filtros baseados no usuário logado
        if current_user:
            query = apply_subscriber_filter(query, current_user, ArduinoDevice)
        
        return query.first()
    
    @staticmethod
    def get_device_by_device_id(db: Session, device_id: str) -> Optional[ArduinoDevice]:
        """
        Busca um dispositivo Arduino pelo identificador único
        
        Args:
            db: Sessão do banco de dados
            device_id: Identificador único do dispositivo
            
        Returns:
            Optional[ArduinoDevice]: Dispositivo encontrado ou None
        """
        return db.query(ArduinoDevice).filter(ArduinoDevice.device_id == device_id).first()
    
    @staticmethod
    def get_device_by_mac(db: Session, mac_address: str) -> Optional[ArduinoDevice]:
        """
        Busca um dispositivo Arduino pelo endereço MAC
        
        Args:
            db: Sessão do banco de dados
            mac_address: Endereço MAC do dispositivo
            
        Returns:
            Optional[ArduinoDevice]: Dispositivo encontrado ou None
        """
        return db.query(ArduinoDevice).filter(ArduinoDevice.mac_address == mac_address).first()
    
    @staticmethod
    def validate_subscriber(db: Session, subscriber_id: uuid.UUID) -> Subscriber:
        """
        Valida se o assinante existe
        
        Args:
            db: Sessão do banco de dados
            subscriber_id: ID do assinante
            
        Returns:
            Subscriber: Assinante encontrado
            
        Raises:
            HTTPException: Se o assinante não for encontrado
        """
        subscriber = db.query(Subscriber).filter(
            Subscriber.id == subscriber_id,
            Subscriber.is_active == True
        ).first()
        
        if not subscriber:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assinante não encontrado ou inativo"
            )
        
        return subscriber
    
    @staticmethod
    def validate_subscriber_by_code(db: Session, subscriber_code: str) -> Subscriber:
        """
        Valida se o assinante existe pelo documento (CPF/CNPJ)
        
        Args:
            db: Sessão do banco de dados
            subscriber_code: Documento do assinante (CPF/CNPJ)
            
        Returns:
            Subscriber: Assinante encontrado
            
        Raises:
            HTTPException: Se o assinante não for encontrado
        """
        subscriber = db.query(Subscriber).filter(
            Subscriber.document == subscriber_code,
            Subscriber.is_active == True
        ).first()
        
        if not subscriber:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assinante não encontrado ou inativo. Verifique o código (CPF/CNPJ) informado."
            )
        
        return subscriber
    
    @staticmethod
    def create_device(db: Session, device_data: ArduinoDeviceCreate) -> ArduinoDevice:
        """
        Cria um novo dispositivo Arduino
        
        Args:
            db: Sessão do banco de dados
            device_data: Dados do novo dispositivo
            
        Returns:
            ArduinoDevice: Dispositivo criado
            
        Raises:
            HTTPException: Se o device_id ou MAC já estiver em uso ou se o assinante não for encontrado
        """
        # Verificar se o ID do dispositivo já está em uso
        existing_id = ArduinoDeviceService.get_device_by_device_id(db, device_data.device_id)
        if existing_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"ID de dispositivo '{device_data.device_id}' já está em uso"
            )
        
        # Verificar se o MAC já está em uso
        existing_mac = ArduinoDeviceService.get_device_by_mac(db, device_data.mac_address)
        if existing_mac:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Endereço MAC '{device_data.mac_address}' já está em uso"
            )
        
        # Verificar se o assinante existe
        ArduinoDeviceService.validate_subscriber(db, device_data.subscriber_id)
        
        # Criar o dispositivo
        new_device = ArduinoDevice(
            device_id=device_data.device_id,
            name=device_data.name,
            description=device_data.description,
            mac_address=device_data.mac_address,
            firmware_version=device_data.firmware_version,
            subscriber_id=device_data.subscriber_id,
            is_active=True
        )
        
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        
        return new_device
    
    @staticmethod
    def create_device_public(db: Session, device_data: dict) -> ArduinoDevice:
        """
        Cria um novo dispositivo Arduino a partir da API pública
        
        Args:
            db: Sessão do banco de dados
            device_data: Dados do novo dispositivo
            
        Returns:
            ArduinoDevice: Dispositivo criado
            
        Raises:
            HTTPException: Se o device_id ou MAC já estiver em uso ou se o assinante não for encontrado
        """
        # Verificar se o ID do dispositivo já está em uso
        existing_id = ArduinoDeviceService.get_device_by_device_id(db, device_data["device_id"])
        if existing_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"ID de dispositivo '{device_data['device_id']}' já está em uso"
            )
        
        # Verificar se o MAC já está em uso
        existing_mac = ArduinoDeviceService.get_device_by_mac(db, device_data["mac_address"])
        if existing_mac:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Endereço MAC '{device_data['mac_address']}' já está em uso"
            )
        
        # Buscar o assinante pelo código
        subscriber = ArduinoDeviceService.validate_subscriber_by_code(db, device_data["subscriber_code"])
        
        # Criar o dispositivo
        new_device = ArduinoDevice(
            device_id=device_data["device_id"],
            name=device_data["name"],
            description=device_data.get("description"),
            mac_address=device_data["mac_address"],
            firmware_version=device_data.get("firmware_version"),
            subscriber_id=subscriber.id,
            is_active=True
        )
        
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        
        return new_device
    
    @staticmethod
    def update_device(db: Session, device_id: uuid.UUID, device_data: ArduinoDeviceUpdate, current_user: Optional["User"] = None) -> Optional[ArduinoDevice]:
        """
        Atualiza um dispositivo Arduino existente
        
        Args:
            db: Sessão do banco de dados
            device_id: ID do dispositivo a ser atualizado
            device_data: Dados a serem atualizados
            current_user: Usuário autenticado (para aplicar filtro por subscriber_id)
            
        Returns:
            Optional[ArduinoDevice]: Dispositivo atualizado ou None se não for encontrado
            
        Raises:
            HTTPException: Se o MAC já estiver em uso por outro dispositivo
        """
        # Buscar o dispositivo pelo ID
        device = ArduinoDeviceService.get_device_by_id(db, device_id, current_user=current_user)
        if not device:
            return None
        
        # Verificar se o MAC já está em uso por outro dispositivo
        if device_data.mac_address and device_data.mac_address != device.mac_address:
            existing_mac = ArduinoDeviceService.get_device_by_mac(db, device_data.mac_address)
            if existing_mac and existing_mac.id != device_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Endereço MAC '{device_data.mac_address}' já está em uso por outro dispositivo"
                )
        
        # Atualizar os campos
        if device_data.name is not None:
            device.name = device_data.name
        
        if device_data.description is not None:
            device.description = device_data.description
        
        if device_data.mac_address is not None:
            device.mac_address = device_data.mac_address
        
        if device_data.ip_address is not None:
            device.ip_address = device_data.ip_address
        
        if device_data.firmware_version is not None:
            device.firmware_version = device_data.firmware_version
        
        if device_data.is_active is not None:
            device.is_active = device_data.is_active
        
        device.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(device)
        
        return device
    
    @staticmethod
    def update_device_connection(db: Session, device_id_or_mac: str, ip_address: str) -> Optional[ArduinoDevice]:
        """
        Atualiza informações de conexão de um dispositivo Arduino
        
        Args:
            db: Sessão do banco de dados
            device_id_or_mac: ID ou MAC do dispositivo
            ip_address: Endereço IP atual do dispositivo
            
        Returns:
            Optional[ArduinoDevice]: Dispositivo atualizado ou None se não for encontrado
        """
        # Buscar o dispositivo pelo ID ou MAC
        device = db.query(ArduinoDevice).filter(
            or_(
                ArduinoDevice.device_id == device_id_or_mac,
                ArduinoDevice.mac_address == device_id_or_mac
            ),
            ArduinoDevice.is_active == True
        ).first()
        
        if not device:
            return None
        
        # Atualizar informações de conexão
        device.ip_address = ip_address
        device.last_connection = datetime.utcnow()
        
        db.commit()
        db.refresh(device)
        
        return device
    
    @staticmethod
    def delete_device(db: Session, device_id: uuid.UUID, current_user: Optional["User"] = None) -> bool:
        """
        Exclui um dispositivo Arduino pelo ID
        
        Args:
            db: Sessão do banco de dados
            device_id: ID do dispositivo a ser excluído
            current_user: Usuário autenticado (para aplicar filtro por subscriber_id)
            
        Returns:
            bool: True se o dispositivo foi excluído, False se não foi encontrado
        """
        # Buscar o dispositivo pelo ID
        device = ArduinoDeviceService.get_device_by_id(db, device_id, current_user=current_user)
        if not device:
            return False
        
        # Excluir o dispositivo
        db.delete(device)
        db.commit()
        
        return True
    
    @staticmethod
    def toggle_device_status(db: Session, device_id: uuid.UUID, activate: bool, current_user: Optional["User"] = None) -> Optional[ArduinoDevice]:
        """
        Ativa ou desativa um dispositivo Arduino
        
        Args:
            db: Sessão do banco de dados
            device_id: ID do dispositivo
            activate: True para ativar, False para desativar
            current_user: Usuário autenticado (para aplicar filtro por subscriber_id)
            
        Returns:
            Optional[ArduinoDevice]: Dispositivo atualizado ou None se não for encontrado
        """
        # Buscar o dispositivo pelo ID
        device = ArduinoDeviceService.get_device_by_id(db, device_id, current_user=current_user)
        if not device:
            return None
        
        # Atualizar o status
        device.is_active = activate
        device.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(device)
        
        return device