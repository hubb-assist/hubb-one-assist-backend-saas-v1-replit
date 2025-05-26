"""
Implementação fake do repositório de pacientes para testes unitários.
"""
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime

from fastapi import HTTPException, status

from app.domain.patient.interfaces import PatientRepository
from app.domain.patient.entities import PatientEntity
from app.schemas.patient import PatientCreate, PatientUpdate


class FakePatientRepository(PatientRepository):
    """
    Implementação fake do repositório de pacientes para testes.
    Utiliza armazenamento em memória para simular o banco de dados.
    """
    
    def __init__(self):
        """
        Inicializa o repositório fake com um dicionário vazio.
        """
        # Dicionário para simular o banco de dados
        # Chave: ID do paciente, Valor: Entidade PatientEntity
        self.patients: Dict[UUID, PatientEntity] = {}
    
    def create(self, patient_data: PatientCreate, subscriber_id: UUID) -> PatientEntity:
        """
        Cria um novo paciente no repositório fake.
        
        Args:
            patient_data: Dados do paciente a ser criado
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            PatientEntity: Entidade de paciente criada
        """
        # Verificar se já existe um paciente com o mesmo CPF para este assinante
        for patient in self.patients.values():
            if (
                patient.cpf == patient_data.cpf and 
                patient.subscriber_id == subscriber_id and
                patient.is_active
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe um paciente ativo com o CPF {patient_data.cpf}"
                )
        
        # Criar nova entidade de paciente
        patient_dict = patient_data.dict()
        patient = PatientEntity(
            id=None,  # ID será gerado automaticamente
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
            subscriber_id=subscriber_id,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Armazenar no dicionário
        self.patients[patient.id] = patient
        
        return patient
    
    def get_by_id(self, patient_id: UUID, subscriber_id: UUID) -> Optional[PatientEntity]:
        """
        Busca um paciente pelo seu ID.
        
        Args:
            patient_id: ID do paciente a ser buscado
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            Optional[PatientEntity]: Entidade de paciente se encontrada, None caso contrário
        """
        patient = self.patients.get(patient_id)
        
        # Verificar se existe e pertence ao assinante correto
        if not patient or patient.subscriber_id != subscriber_id:
            return None
            
        return patient
    
    def update(self, patient_id: UUID, patient_data: PatientUpdate, subscriber_id: UUID) -> PatientEntity:
        """
        Atualiza um paciente existente.
        
        Args:
            patient_id: ID do paciente a ser atualizado
            patient_data: Dados do paciente para atualização
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            PatientEntity: Entidade de paciente atualizada
            
        Raises:
            HTTPException: Se o paciente não for encontrado
        """
        # Buscar paciente existente
        patient = self.get_by_id(patient_id, subscriber_id)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente com ID {patient_id} não encontrado"
            )
        
        # Verificar se está tentando atualizar para um CPF já existente
        if patient_data.cpf is not None and patient_data.cpf != patient.cpf:
            for existing in self.patients.values():
                if (
                    existing.cpf == patient_data.cpf and 
                    existing.subscriber_id == subscriber_id and
                    existing.id != patient_id and
                    existing.is_active
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Já existe um paciente ativo com o CPF {patient_data.cpf}"
                    )
        
        # Atualizar campos
        update_data = patient_data.dict(exclude_unset=True)
        
        # Atualizar informações pessoais
        if "name" in update_data or "cpf" in update_data or "rg" in update_data or "birth_date" in update_data:
            patient.update_personal_info(
                name=update_data.get("name"),
                cpf=update_data.get("cpf"),
                rg=update_data.get("rg"),
                birth_date=update_data.get("birth_date")
            )
            
        # Atualizar contato
        if "phone" in update_data:
            patient.update_contact_info(phone=update_data.get("phone"))
            
        # Atualizar endereço
        address_fields = {
            "zip_code", "address", "number", "complement", 
            "district", "city", "state"
        }
        
        if any(field in update_data for field in address_fields):
            patient.update_address(
                zip_code=update_data.get("zip_code"),
                address=update_data.get("address"),
                number=update_data.get("number"),
                complement=update_data.get("complement"),
                district=update_data.get("district"),
                city=update_data.get("city"),
                state=update_data.get("state")
            )
            
        # Ativar/desativar
        if "is_active" in update_data:
            if update_data["is_active"]:
                patient.activate()
            else:
                patient.deactivate()
                
        return patient
    
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
        # Filtrar pelo subscriber_id
        filtered_patients = [
            p for p in self.patients.values() 
            if p.subscriber_id == subscriber_id
        ]
        
        # Aplicar filtros adicionais
        if "name" in filters and filters["name"]:
            name_filter = filters["name"].lower()
            filtered_patients = [
                p for p in filtered_patients 
                if p.name and name_filter in p.name.lower()
            ]
            
        if "cpf" in filters and filters["cpf"]:
            cpf_filter = filters["cpf"].lower()
            filtered_patients = [
                p for p in filtered_patients 
                if p.cpf and cpf_filter in p.cpf.lower()
            ]
            
        # Ordenar por nome
        filtered_patients.sort(key=lambda p: p.name if p.name else "")
        
        # Contar total
        total = len(filtered_patients)
        
        # Aplicar paginação
        paginated_patients = filtered_patients[skip:skip + limit]
        
        # Retornar resultado paginado
        return {
            "items": paginated_patients,
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
            
        Raises:
            HTTPException: Se o paciente não for encontrado
        """
        patient = self.get_by_id(patient_id, subscriber_id)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente com ID {patient_id} não encontrado"
            )
            
        # Desativar o paciente
        patient.deactivate()
        
        return True