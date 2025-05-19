"""
Provedores de dependência para injeção via FastAPI.
Segue o Princípio de Inversão de Dependência (DIP).
"""
from typing import Callable, Type, TypeVar

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.patient.interfaces import PatientRepository
from app.infrastructure.repositories.patient_repository import PatientSQLAlchemyRepository

# Tipo genérico para repositórios
T = TypeVar('T')


def get_patient_repository(db: Session = Depends(get_db)) -> PatientRepository:
    """
    Provê uma implementação concreta de PatientRepository.
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        PatientRepository: Uma implementação concreta da interface PatientRepository
    """
    return PatientSQLAlchemyRepository(db)


def get_repository(repo_type: Type[T], db: Session = Depends(get_db)) -> T:
    """
    Função genérica para prover qualquer tipo de repositório.
    
    Args:
        repo_type: Tipo de repositório a ser provido
        db: Sessão do banco de dados
        
    Returns:
        T: Uma implementação concreta do tipo de repositório solicitado
    """
    repos = {
        PatientRepository: PatientSQLAlchemyRepository(db),
        # Adicionar outros repositórios aqui conforme necessário
    }
    
    return repos.get(repo_type)