"""
Adaptador para converter entre entidades de domínio e modelos ORM para pacientes.
"""
from app.domain.patient.entities import PatientEntity
from app.db.models import Patient


class PatientAdapter:
    """
    Classe adaptadora que converte entre PatientEntity (domínio) e Patient (ORM).
    """
    
    @staticmethod
    def to_entity(orm_model: Patient) -> PatientEntity:
        """
        Converte um modelo ORM de paciente em uma entidade de domínio.
        
        Args:
            orm_model: Modelo ORM de Patient
            
        Returns:
            PatientEntity: Entidade de domínio equivalente
        """
        if not orm_model:
            return None
            
        return PatientEntity(
            id=orm_model.id,
            name=orm_model.name,
            cpf=orm_model.cpf,
            rg=orm_model.rg,
            birth_date=orm_model.birth_date,
            phone=orm_model.phone,
            zip_code=orm_model.zip_code,
            address=orm_model.address,
            number=orm_model.number,
            complement=orm_model.complement,
            district=orm_model.district,
            city=orm_model.city,
            state=orm_model.state,
            subscriber_id=orm_model.subscriber_id,
            is_active=orm_model.is_active,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at
        )
    
    @staticmethod
    def to_orm_model(entity: PatientEntity, orm_model: Patient = None) -> Patient:
        """
        Converte uma entidade de domínio para um modelo ORM.
        Se um modelo ORM for fornecido, apenas atualiza seus atributos.
        
        Args:
            entity: Entidade de domínio de paciente
            orm_model: Modelo ORM opcional para atualizar (em vez de criar)
            
        Returns:
            Patient: Modelo ORM atualizado ou criado
        """
        if not entity:
            return None
            
        if not orm_model:
            # Criar novo modelo ORM
            orm_model = Patient(
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
        else:
            # Atualizar modelo existente
            orm_model.name = entity.name
            orm_model.cpf = entity.cpf
            orm_model.rg = entity.rg
            orm_model.birth_date = entity.birth_date
            orm_model.phone = entity.phone
            orm_model.zip_code = entity.zip_code
            orm_model.address = entity.address
            orm_model.number = entity.number
            orm_model.complement = entity.complement
            orm_model.district = entity.district
            orm_model.city = entity.city
            orm_model.state = entity.state
            orm_model.is_active = entity.is_active
            orm_model.updated_at = entity.updated_at
        
        return orm_model