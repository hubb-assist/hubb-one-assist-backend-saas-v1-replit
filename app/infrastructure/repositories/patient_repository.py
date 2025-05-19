"""
Implementação concreta do repositório de pacientes usando SQLAlchemy.
"""
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.domain.patient.interfaces import PatientRepository
from app.domain.patient.entities import PatientEntity
from app.db.models import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


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
    
    def _entity_to_orm(self, entity: PatientEntity) -> Patient:
        """
        Converte uma entidade de domínio para um modelo ORM.
        
        Args:
            entity: Entidade de paciente
            
        Returns:
            Patient: Modelo ORM de paciente
        """
        return Patient(
            id=entity.id,
            name=entity.name,
            cpf=entity.cpf,
            rg=entity.rg,
            birth_date=entity.birth_date,
            phone=entity.phone,
            zip_code=entity.zip_code,
            address=entity.address,
            number=entity.number,
            complement=entity.complement,
            district=entity.district,
            city=entity.city,
            state=entity.state,
            subscriber_id=entity.subscriber_id,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def _orm_to_entity(self, orm: Patient) -> PatientEntity:
        """
        Converte um modelo ORM para uma entidade de domínio.
        
        Args:
            orm: Modelo ORM de paciente
            
        Returns:
            PatientEntity: Entidade de paciente
        """
        # Precisamos obter os valores reais dos atributos, não as colunas SQLAlchemy
        return PatientEntity(
            id=getattr(orm, 'id', None),
            name=getattr(orm, 'name', ""),
            cpf=getattr(orm, 'cpf', ""),
            rg=getattr(orm, 'rg', None),
            birth_date=getattr(orm, 'birth_date', None),
            phone=getattr(orm, 'phone', None),
            zip_code=getattr(orm, 'zip_code', None),
            address=getattr(orm, 'address', None),
            number=getattr(orm, 'number', None),
            complement=getattr(orm, 'complement', None),
            district=getattr(orm, 'district', None),
            city=getattr(orm, 'city', None),
            state=getattr(orm, 'state', None),
            subscriber_id=getattr(orm, 'subscriber_id', None),
            is_active=getattr(orm, 'is_active', True),
            created_at=getattr(orm, 'created_at', None),
            updated_at=getattr(orm, 'updated_at', None)
        )
    
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
        
        # Criar primeiro como entidade de domínio
        patient_entity = PatientEntity(
            name=patient_dict["name"],
            cpf=patient_dict["cpf"],
            rg=patient_dict.get("rg"),
            birth_date=patient_dict["birth_date"],
            phone=patient_dict.get("phone"),
            zip_code=patient_dict.get("zip_code"),
            address=patient_dict.get("address"),
            number=patient_dict.get("number"),
            complement=patient_dict.get("complement"),
            district=patient_dict.get("district"),
            city=patient_dict.get("city"),
            state=patient_dict.get("state"),
            subscriber_id=subscriber_id
        )
        
        # Converter para modelo ORM e salvar
        patient_orm = self._entity_to_orm(patient_entity)
        self.db.add(patient_orm)
        self.db.commit()
        self.db.refresh(patient_orm)
        
        # Retornar como entidade de domínio
        return self._orm_to_entity(patient_orm)
    
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
        
        return self._orm_to_entity(patient)
    
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
        
        # Converter para entidade de domínio
        patient_entity = self._orm_to_entity(patient)
        
        # Atualizar apenas campos não-nulos
        update_data = patient_data.dict(exclude_unset=True)
        
        # Atualizar campos básicos de identificação e contato
        if "name" in update_data:
            patient_entity.update_personal_info(name=update_data["name"])
        if "cpf" in update_data:
            patient_entity.update_personal_info(cpf=update_data["cpf"])
        if "rg" in update_data:
            patient_entity.update_personal_info(rg=update_data["rg"])
        if "birth_date" in update_data:
            patient_entity.update_personal_info(birth_date=update_data["birth_date"])
        if "phone" in update_data:
            patient_entity.update_contact_info(phone=update_data["phone"])
        
        # Atualizar campos de endereço
        address_fields = {
            "zip_code": update_data.get("zip_code"),
            "address": update_data.get("address"),
            "number": update_data.get("number"),
            "complement": update_data.get("complement"),
            "district": update_data.get("district"),
            "city": update_data.get("city"),
            "state": update_data.get("state")
        }
        
        # Se qualquer campo de endereço foi fornecido, atualizar
        if any(v is not None for v in address_fields.values()):
            # Filtrar apenas os campos que foram fornecidos
            address_update = {k: v for k, v in address_fields.items() if v is not None}
            patient_entity.update_address(**address_update)
        
        # Ativar/desativar paciente
        if "is_active" in update_data:
            if update_data["is_active"]:
                patient_entity.activate()
            else:
                patient_entity.deactivate()
        
        # Atualizar modelo ORM com os dados da entidade
        for attr, value in vars(patient_entity).items():
            setattr(patient, attr, value)
        
        self.db.commit()
        self.db.refresh(patient)
        
        return self._orm_to_entity(patient)
    
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
        patients_entities = [self._orm_to_entity(p) for p in patients_orm]
        
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
        
        # Transformar em entidade e desativar
        patient_entity = self._orm_to_entity(patient)
        patient_entity.deactivate()
        
        # Aplicar alteração no modelo ORM
        patient.is_active = patient_entity.is_active
        patient.updated_at = patient_entity.updated_at
        
        self.db.commit()
        
        return True