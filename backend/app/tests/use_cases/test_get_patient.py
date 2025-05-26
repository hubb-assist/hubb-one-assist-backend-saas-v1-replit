"""
Testes unitários para o caso de uso GetPatientUseCase.
"""
import uuid
from datetime import date

import pytest

from app.application.use_cases.patient.get_patient import GetPatientUseCase
from app.tests.fakes.fake_patient_repository import FakePatientRepository
from app.domain.patient.entities import PatientEntity


class TestGetPatientUseCase:
    """
    Testes para o caso de uso de busca de paciente por ID.
    """
    
    def setup_method(self):
        """
        Configuração antes de cada teste.
        """
        # Inicializar o repositório fake
        self.repository = FakePatientRepository()
        
        # Inicializar o caso de uso com o repositório fake
        self.use_case = GetPatientUseCase(self.repository)
        
        # IDs para uso nos testes
        self.subscriber_id = uuid.uuid4()
        self.patient_id = uuid.uuid4()
        
        # Adicionar um paciente para testes
        self.test_patient = PatientEntity(
            id=self.patient_id,
            name="Teste da Silva",
            cpf="123.456.789-00",
            birth_date=date(1980, 1, 1),
            subscriber_id=self.subscriber_id
        )
        
        # Adicionar diretamente ao repositório
        self.repository.patients[self.patient_id] = self.test_patient
    
    def test_get_existing_patient(self):
        """
        Testa a busca de um paciente que existe no repositório.
        """
        # Executar o caso de uso
        patient = self.use_case.execute(self.patient_id, self.subscriber_id)
        
        # Verificar se o paciente foi encontrado
        assert patient is not None
        assert patient.id == self.patient_id
        assert patient.name == "Teste da Silva"
        assert patient.cpf == "123.456.789-00"
        assert patient.birth_date == date(1980, 1, 1)
        assert patient.subscriber_id == self.subscriber_id
    
    def test_get_nonexistent_patient(self):
        """
        Testa a busca de um paciente que não existe no repositório.
        """
        # ID inexistente
        nonexistent_id = uuid.uuid4()
        
        # Executar o caso de uso
        patient = self.use_case.execute(nonexistent_id, self.subscriber_id)
        
        # Verificar que retornou None
        assert patient is None
    
    def test_get_patient_wrong_subscriber(self):
        """
        Testa a busca de um paciente com o ID de assinante incorreto.
        """
        # ID de assinante diferente
        other_subscriber_id = uuid.uuid4()
        
        # Executar o caso de uso
        patient = self.use_case.execute(self.patient_id, other_subscriber_id)
        
        # Verificar que retornou None (segurança multitenancy)
        assert patient is None