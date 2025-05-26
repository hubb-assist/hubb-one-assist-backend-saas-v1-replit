"""
Serviço para gerenciamento de pacientes no sistema HUBB ONE Assist
"""
from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


class PatientService:
    """
    Classe de serviço para operações relacionadas a pacientes
    """
    @staticmethod
    def create_patient(db: Session, patient_data: PatientCreate, subscriber_id: UUID) -> Patient:
        """
        Cria um novo paciente no sistema
        
        Args:
            db: Sessão do banco de dados
            patient_data: Dados do paciente a ser criado
            subscriber_id: ID do assinante (subscriber) ao qual o paciente pertence
            
        Returns:
            Patient: Objeto do paciente criado
        """
        patient_dict = patient_data.dict()
        patient = Patient(**patient_dict, subscriber_id=subscriber_id)
        
        db.add(patient)
        db.commit()
        db.refresh(patient)
        
        return patient
    
    @staticmethod
    def get_patient(db: Session, patient_id: UUID, subscriber_id: UUID) -> Optional[Patient]:
        """
        Busca um paciente pelo ID com verificação de tenant
        
        Args:
            db: Sessão do banco de dados
            patient_id: ID do paciente
            subscriber_id: ID do assinante para verificação multitenant
            
        Returns:
            Optional[Patient]: Objeto do paciente, se encontrado
        """
        patient = db.query(Patient).filter(
            Patient.id == patient_id,
            Patient.subscriber_id == subscriber_id,
            Patient.is_active == True
        ).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente não encontrado"
            )
            
        return patient
    
    @staticmethod
    def list_patients(
        db: Session, 
        subscriber_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        name: Optional[str] = None,
        cpf: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lista os pacientes com opções de paginação e filtros
        
        Args:
            db: Sessão do banco de dados
            subscriber_id: ID do assinante para filtro multitenant
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros a retornar
            name: Filtro opcional por nome (contém)
            cpf: Filtro opcional por CPF (contém)
            
        Returns:
            Dict: Dicionário com resultados paginados e metadados
        """
        # Query base
        query = db.query(Patient).filter(
            Patient.subscriber_id == subscriber_id,
            Patient.is_active == True
        )
        
        # Aplicar filtros opcionais
        if name:
            query = query.filter(Patient.name.ilike(f"%{name}%"))
        
        if cpf:
            query = query.filter(Patient.cpf.ilike(f"%{cpf}%"))
        
        # Contar total antes da paginação
        total = query.count()
        
        # Aplicar paginação
        patients = query.order_by(Patient.name).offset(skip).limit(limit).all()
        
        # Calcular metadados de paginação
        return {
            "items": patients,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    
    @staticmethod
    def update_patient(
        db: Session, 
        patient_id: UUID, 
        patient_data: PatientUpdate, 
        subscriber_id: UUID
    ) -> Patient:
        """
        Atualiza os dados de um paciente existente
        
        Args:
            db: Sessão do banco de dados
            patient_id: ID do paciente a ser atualizado
            patient_data: Dados do paciente para atualização
            subscriber_id: ID do assinante para verificação multitenant
            
        Returns:
            Patient: Objeto do paciente atualizado
        """
        patient = PatientService.get_patient(db, patient_id, subscriber_id)
        
        # Atualizar apenas campos não-nulos
        update_data = patient_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:  # Não atualiza campos explicitamente definidos como None
                setattr(patient, key, value)
        
        db.commit()
        db.refresh(patient)
        return patient
    
    @staticmethod
    def delete_patient(db: Session, patient_id: UUID, subscriber_id: UUID) -> Dict[str, str]:
        """
        Remove logicamente um paciente (soft delete)
        
        Args:
            db: Sessão do banco de dados
            patient_id: ID do paciente a ser removido
            subscriber_id: ID do assinante para verificação multitenant
            
        Returns:
            Dict: Mensagem de confirmação
        """
        patient = PatientService.get_patient(db, patient_id, subscriber_id)
        
        # Deleção lógica
        patient.is_active = False
        
        db.commit()
        return {"message": "Paciente removido com sucesso"}