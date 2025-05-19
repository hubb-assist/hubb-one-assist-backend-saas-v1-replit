"""
Adaptador para converter entre entidades de domínio e modelos ORM para pacientes.
"""
from typing import Optional, Any, get_type_hints
from app.domain.patient.entities import PatientEntity
from app.db.models import Patient


class PatientAdapter:
    """
    Classe adaptadora que converte entre PatientEntity (domínio) e Patient (ORM).
    Lida com a conversão entre modelos de dados simples (ORM) e entidades ricas
    com Value Objects.
    """
    
    @staticmethod
    def to_entity(orm_model: Patient) -> Optional[PatientEntity]:
        """
        Converte um modelo ORM de paciente em uma entidade de domínio.
        
        Args:
            orm_model: Modelo ORM de Patient
            
        Returns:
            Optional[PatientEntity]: Entidade de domínio equivalente ou None
        """
        if not orm_model:
            return None
            
        # Extrair valores dos atributos do modelo ORM
        # usando getattr para lidar com a diferença entre Column e valor
        return PatientEntity(
            id=getattr(orm_model, 'id', None),
            name=str(getattr(orm_model, 'name', "")),
            cpf=str(getattr(orm_model, 'cpf', "")),
            rg=str(getattr(orm_model, 'rg', "")) if getattr(orm_model, 'rg', None) else None,
            birth_date=getattr(orm_model, 'birth_date', None),
            phone=str(getattr(orm_model, 'phone', "")) if getattr(orm_model, 'phone', None) else None,
            zip_code=str(getattr(orm_model, 'zip_code', "")) if getattr(orm_model, 'zip_code', None) else None,
            address=str(getattr(orm_model, 'address', "")) if getattr(orm_model, 'address', None) else None,
            number=str(getattr(orm_model, 'number', "")) if getattr(orm_model, 'number', None) else None,
            complement=str(getattr(orm_model, 'complement', "")) if getattr(orm_model, 'complement', None) else None,
            district=str(getattr(orm_model, 'district', "")) if getattr(orm_model, 'district', None) else None,
            city=str(getattr(orm_model, 'city', "")) if getattr(orm_model, 'city', None) else None,
            state=str(getattr(orm_model, 'state', "")) if getattr(orm_model, 'state', None) else None,
            subscriber_id=getattr(orm_model, 'subscriber_id', None),
            is_active=bool(getattr(orm_model, 'is_active', True)),
            created_at=getattr(orm_model, 'created_at', None),
            updated_at=getattr(orm_model, 'updated_at', None)
        )
    
    @staticmethod
    def to_orm_model(entity: PatientEntity, orm_model: Patient = None) -> Patient:
        """
        Converte uma entidade de domínio para um modelo ORM.
        Se um modelo ORM for fornecido, apenas atualiza seus atributos.
        Extrai informações de Value Objects para campos simples do ORM.
        
        Args:
            entity: Entidade de domínio de paciente
            orm_model: Modelo ORM opcional para atualizar (em vez de criar)
            
        Returns:
            Patient: Modelo ORM atualizado ou criado
        """
        if not entity:
            return None
            
        # Extrair valores dos Value Objects para formato simples
        # adequado ao modelo ORM
        patient_data = {
            'id': entity.id,
            'name': entity.name,
            'cpf': entity.cpf,  # Já formatado pela property
            'rg': entity.rg,
            'birth_date': entity.birth_date,
            'phone': entity.phone,  # Já formatado pela property
            'zip_code': entity.zip_code,
            'address': entity.address,
            'number': entity.number,
            'complement': entity.complement,
            'district': entity.district,
            'city': entity.city,
            'state': entity.state,
            'subscriber_id': entity.subscriber_id,
            'is_active': entity.is_active,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
            
        if not orm_model:
            # Criar novo modelo ORM
            orm_model = Patient(**patient_data)
        else:
            # Atualizar modelo existente
            for key, value in patient_data.items():
                # Não atualizar o ID ou campos de auditoria de criação
                if key != 'id' and key != 'created_at':
                    setattr(orm_model, key, value)
        
        return orm_model
    
    @staticmethod
    def extract_simple_data(entity: PatientEntity) -> dict:
        """
        Extrai dados simples de uma entidade rica com Value Objects.
        Útil para serialização e APIs.
        
        Args:
            entity: Entidade de domínio de paciente
            
        Returns:
            dict: Dados em formato simples adequado para JSON
        """
        return {
            'id': str(entity.id),
            'name': entity.name,
            'cpf': entity.cpf,
            'cpf_unformatted': entity.cpf_unformatted,
            'rg': entity.rg,
            'birth_date': entity.birth_date.isoformat() if entity.birth_date else None,
            'phone': entity.phone,
            'phone_unformatted': entity.phone_unformatted,
            'zip_code': entity.zip_code,
            'address': entity.address,
            'number': entity.number,
            'complement': entity.complement,
            'district': entity.district,
            'city': entity.city,
            'state': entity.state,
            'full_address': entity.full_address,
            'subscriber_id': str(entity.subscriber_id) if entity.subscriber_id else None,
            'is_active': entity.is_active,
            'created_at': entity.created_at.isoformat() if entity.created_at else None,
            'updated_at': entity.updated_at.isoformat() if entity.updated_at else None
        }