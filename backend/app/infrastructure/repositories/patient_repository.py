"""
Implementação concreta do repositório de pacientes usando SQLAlchemy.
"""
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from app.domain.patient.interfaces import PatientRepository
from app.domain.patient.entities import PatientEntity
from app.db.models import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from app.infrastructure.adapters.patient_adapter import PatientAdapter


class PatientSQLAlchemyRepository(PatientRepository):
    """
    Implementação do repositório de pacientes usando SQLAlchemy.
    Esta classe é responsável por traduzir entre entidades de domínio e modelos ORM.
    """
    
    def __init__(self, db: Session):
        """
        Inicializa o repositório com uma sessão do banco de dados.
        
        Args:
            db: Sessão do SQLAlchemy
        """
        self.db = db
    
    def create(self, patient_data: PatientCreate, subscriber_id: UUID) -> PatientEntity:
        """
        Cria um novo paciente no banco de dados.
        
        Args:
            patient_data: Dados do paciente a ser criado
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            PatientEntity: Entidade de paciente criada
        """
        # Verificar se já existe um paciente com o mesmo CPF para este assinante
        existing_patient = self.db.query(Patient).filter(
            Patient.cpf == patient_data.cpf,
            Patient.subscriber_id == subscriber_id,
            Patient.is_active == True
        ).first()
        
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe um paciente ativo com o CPF {patient_data.cpf}"
            )
        
        # Criar novo paciente a partir dos dados do schema
        patient_dict = patient_data.dict()
        patient_dict["subscriber_id"] = subscriber_id
        
        # Criar modelo ORM
        patient_orm = Patient(**patient_dict)
        
        self.db.add(patient_orm)
        self.db.commit()
        self.db.refresh(patient_orm)
        
        # Converter para entidade de domínio usando o adaptador
        patient_entity = PatientAdapter.to_entity(patient_orm)
        if patient_entity is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao processar o paciente criado"
            )
            
        return patient_entity
    
    def get_by_id(self, patient_id: UUID, subscriber_id: UUID) -> Optional[PatientEntity]:
        """
        Busca um paciente pelo seu ID.
        
        Args:
            patient_id: ID do paciente a ser buscado
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            Optional[PatientEntity]: Entidade de paciente se encontrada, None caso contrário
        """
        patient = self.db.query(Patient).filter(
            Patient.id == patient_id,
            Patient.subscriber_id == subscriber_id
        ).first()
        
        if not patient:
            return None
        
        return PatientAdapter.to_entity(patient)
    
    def update(self, patient_id: UUID, patient_data: PatientUpdate, subscriber_id: UUID) -> PatientEntity:
        """
        Atualiza um paciente existente.
        
        Args:
            patient_id: ID do paciente a ser atualizado
            patient_data: Dados do paciente para atualização
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            PatientEntity: Entidade de paciente atualizada
        """
        # Buscar paciente existente
        patient = self.db.query(Patient).filter(
            Patient.id == patient_id,
            Patient.subscriber_id == subscriber_id
        ).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente com ID {patient_id} não encontrado"
            )
        
        # Verificar se está tentando atualizar para um CPF já existente
        if patient_data.cpf is not None and patient_data.cpf != patient.cpf:
            existing_patient = self.db.query(Patient).filter(
                Patient.cpf == patient_data.cpf,
                Patient.subscriber_id == subscriber_id,
                Patient.id != patient_id,
                Patient.is_active == True
            ).first()
            
            if existing_patient:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe um paciente ativo com o CPF {patient_data.cpf}"
                )
        
        # Atualizar apenas campos não-nulos
        update_data = patient_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(patient, key):
                setattr(patient, key, value)
        
        # Atualizar timestamp
        patient.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(patient)
        
        # Converter para entidade de domínio e verificar se foi convertido corretamente
        patient_entity = PatientAdapter.to_entity(patient)
        if patient_entity is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao processar o paciente atualizado"
            )
            
        return patient_entity
    
    def list(
        self, 
        subscriber_id: UUID, 
        skip: int = 0, 
        limit: int = 10, 
        **filters
    ) -> Dict[str, Any]:
        """
        Lista pacientes com paginação e filtros.
        
        Args:
            subscriber_id: ID do assinante (isolamento multitenancy)
            skip: Quantidade de registros para pular
            limit: Limite de registros a retornar
            **filters: Filtros adicionais (ex: name, cpf)
            
        Returns:
            Dict[str, Any]: Objeto de resposta com lista de pacientes e metadados de paginação
        """
        # Iniciar query base
        query = self.db.query(Patient).filter(Patient.subscriber_id == subscriber_id)
        
        # Aplicar filtros dinâmicos
        if "name" in filters and filters["name"]:
            query = query.filter(Patient.name.ilike(f"%{filters['name']}%"))
        
        if "cpf" in filters and filters["cpf"]:
            query = query.filter(Patient.cpf.ilike(f"%{filters['cpf']}%"))
        
        # Contar total para paginação
        total = query.count()
        
        # Aplicar paginação
        patients_orm = query.order_by(Patient.name).offset(skip).limit(limit).all()
        
        # Converter para entidades de domínio
        patients_entities = [
            entity for entity in [PatientAdapter.to_entity(p) for p in patients_orm]
            if entity is not None
        ]
        
        # Calcular metadados de paginação
        return {
            "items": patients_entities,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    
    def delete(self, patient_id: UUID, subscriber_id: UUID) -> bool:
        """
        Exclui logicamente um paciente (is_active = False).
        
        Args:
            patient_id: ID do paciente a ser excluído
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        patient = self.db.query(Patient).filter(
            Patient.id == patient_id,
            Patient.subscriber_id == subscriber_id
        ).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente com ID {patient_id} não encontrado"
            )
        
        # Atualizar como inativo
        patient.is_active = False
        patient.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True