from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.domain.anamnesis.interfaces import IAnamnesisRepository
from app.domain.anamnesis.entities import AnamnesisEntity
from app.schemas.anamnesis_schema import AnamnesisCreate, AnamnesisUpdate
from app.db.models_anamnesis import Anamnesis

class AnamnesisSQLAlchemyRepository(IAnamnesisRepository):
    """
    Implementação SQLAlchemy do repositório de anamneses.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, data: AnamnesisCreate, patient_id: UUID, subscriber_id: UUID) -> AnamnesisEntity:
        """
        Cria uma nova anamnese no banco de dados.
        
        Args:
            data: Dados da anamnese
            patient_id: ID do paciente
            subscriber_id: ID do assinante
            
        Returns:
            AnamnesisEntity: Entidade de anamnese criada
        """
        anamnesis_data = data.dict()
        
        # Criar modelo SQLAlchemy
        anamnesis_model = Anamnesis(
            patient_id=patient_id,
            subscriber_id=subscriber_id,
            **anamnesis_data
        )
        
        # Persistir no banco
        self.db.add(anamnesis_model)
        self.db.commit()
        self.db.refresh(anamnesis_model)
        
        # Retornar entidade
        return self._to_entity(anamnesis_model)
    
    def get_by_id(self, id: UUID, subscriber_id: UUID) -> Optional[AnamnesisEntity]:
        """
        Busca uma anamnese pelo ID.
        
        Args:
            id: ID da anamnese
            subscriber_id: ID do assinante
            
        Returns:
            Optional[AnamnesisEntity]: Entidade encontrada ou None
        """
        anamnesis_model = (
            self.db.query(Anamnesis)
            .filter(
                Anamnesis.id == id,
                Anamnesis.subscriber_id == subscriber_id,
                Anamnesis.is_active == True
            )
            .first()
        )
        
        if not anamnesis_model:
            return None
            
        return self._to_entity(anamnesis_model)
        
    def list_by_patient(
        self, patient_id: UUID, subscriber_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AnamnesisEntity]:
        """
        Lista anamneses de um paciente específico.
        
        Args:
            patient_id: ID do paciente
            subscriber_id: ID do assinante
            skip: Quantidade de registros para pular
            limit: Limite de registros a retornar
            
        Returns:
            List[AnamnesisEntity]: Lista de entidades
        """
        anamnesis_models = (
            self.db.query(Anamnesis)
            .filter(
                Anamnesis.patient_id == patient_id,
                Anamnesis.subscriber_id == subscriber_id,
                Anamnesis.is_active == True
            )
            .order_by(Anamnesis.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return [self._to_entity(model) for model in anamnesis_models]
    
    def update(self, id: UUID, data: AnamnesisUpdate, subscriber_id: UUID) -> Optional[AnamnesisEntity]:
        """
        Atualiza uma anamnese existente.
        
        Args:
            id: ID da anamnese
            data: Dados da anamnese para atualização
            subscriber_id: ID do assinante
            
        Returns:
            Optional[AnamnesisEntity]: Entidade atualizada ou None
        """
        anamnesis_model = (
            self.db.query(Anamnesis)
            .filter(
                Anamnesis.id == id,
                Anamnesis.subscriber_id == subscriber_id,
                Anamnesis.is_active == True
            )
            .first()
        )
        
        if not anamnesis_model:
            return None
            
        # Atualizar apenas campos não nulos
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(anamnesis_model, key, value)
            
        self.db.commit()
        self.db.refresh(anamnesis_model)
        
        return self._to_entity(anamnesis_model)
    
    def delete(self, id: UUID, subscriber_id: UUID) -> bool:
        """
        Exclui logicamente uma anamnese.
        
        Args:
            id: ID da anamnese
            subscriber_id: ID do assinante
            
        Returns:
            bool: True se a exclusão foi bem-sucedida
        """
        anamnesis_model = (
            self.db.query(Anamnesis)
            .filter(
                Anamnesis.id == id,
                Anamnesis.subscriber_id == subscriber_id,
                Anamnesis.is_active == True
            )
            .first()
        )
        
        if not anamnesis_model:
            return False
            
        # Exclusão lógica - usando setattr para evitar erros de tipagem com SQLAlchemy
        setattr(anamnesis_model, "is_active", False)
        self.db.commit()
        
        return True
    
    def count_by_patient(self, patient_id: UUID, subscriber_id: UUID) -> int:
        """
        Conta o número de anamneses de um paciente.
        
        Args:
            patient_id: ID do paciente
            subscriber_id: ID do assinante
            
        Returns:
            int: Quantidade de anamneses
        """
        return (
            self.db.query(Anamnesis)
            .filter(
                Anamnesis.patient_id == patient_id,
                Anamnesis.subscriber_id == subscriber_id,
                Anamnesis.is_active == True
            )
            .count()
        )
    
    def _to_entity(self, model: Anamnesis) -> AnamnesisEntity:
        """
        Converte um modelo SQLAlchemy para uma entidade de domínio.
        
        Args:
            model: Modelo SQLAlchemy
            
        Returns:
            AnamnesisEntity: Entidade de domínio
        """
        # Extrair valores do modelo SQLAlchemy para evitar erros de tipagem
        id_value = model.id 
        subscriber_id_value = model.subscriber_id
        patient_id_value = model.patient_id
        chief_complaint_value = model.chief_complaint
        medical_history_value = model.medical_history
        allergies_value = model.allergies
        medications_value = model.medications
        notes_value = model.notes
        is_active_value = model.is_active
        created_at_value = model.created_at
        updated_at_value = model.updated_at
        
        return AnamnesisEntity(
            id=id_value,
            subscriber_id=subscriber_id_value,
            patient_id=patient_id_value,
            chief_complaint=str(chief_complaint_value) if chief_complaint_value is not None else "",
            medical_history=str(medical_history_value) if medical_history_value is not None else None,
            allergies=str(allergies_value) if allergies_value is not None else None,
            medications=str(medications_value) if medications_value is not None else None,
            notes=str(notes_value) if notes_value is not None else None,
            is_active=bool(is_active_value),
            created_at=created_at_value,
            updated_at=updated_at_value
        )