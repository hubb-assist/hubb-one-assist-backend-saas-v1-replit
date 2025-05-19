"""
Testes unitários para o caso de uso CreatePatientUseCase.
"""
import uuid
from datetime import date

import pytest
from fastapi import HTTPException

from app.application.use_cases.patient.create_patient import CreatePatientUseCase
from app.tests.fakes.fake_patient_repository import FakePatientRepository
from app.schemas.patient import PatientCreate


class TestCreatePatientUseCase:
    """
    Testes para o caso de uso de criação de paciente.
    """
    
    def setup_method(self):
        """
        Configuração antes de cada teste.
        """
        # Inicializar o repositório fake
        self.repository = FakePatientRepository()
        
        # Inicializar o caso de uso com o repositório fake
        self.use_case = CreatePatientUseCase(self.repository)
        
        # IDs para uso nos testes
        self.subscriber_id = uuid.uuid4()
        
        # Dados para teste
        self.patient_data = PatientCreate(
            name="João da Silva",
            cpf="123.456.789-10",
            birth_date=date(1980, 1, 1)
        )
    
    def test_create_patient_success(self):
        """
        Testa a criação bem-sucedida de um paciente.
        """
        # Executar o caso de uso
        patient = self.use_case.execute(self.patient_data, self.subscriber_id)
        
        # Verificar se o paciente foi criado corretamente
        assert patient is not None
        assert patient.name == "João da Silva"
        assert patient.cpf == "123.456.789-10"
        assert patient.birth_date == date(1980, 1, 1)
        assert patient.subscriber_id == self.subscriber_id
        assert patient.is_active == True
        
        # Verificar se o paciente foi armazenado no repositório
        assert len(self.repository.patients) == 1
        assert patient.id in self.repository.patients
    
    def test_create_patient_duplicate_cpf(self):
        """
        Testa a tentativa de criar um paciente com CPF duplicado.
        """
        # Criar o primeiro paciente
        self.use_case.execute(self.patient_data, self.subscriber_id)
        
        # Tentar criar um segundo paciente com o mesmo CPF
        duplicate_data = PatientCreate(
            name="Maria da Silva",
            cpf="123.456.789-10",  # Mesmo CPF
            birth_date=date(1985, 5, 5)
        )
        
        # Verificar que uma exceção é lançada
        with pytest.raises(HTTPException) as excinfo:
            self.use_case.execute(duplicate_data, self.subscriber_id)
        
        # Verificar que o código de status e a mensagem estão corretos
        assert excinfo.value.status_code == 400
        assert "Já existe um paciente ativo com o CPF" in excinfo.value.detail
    
    def test_create_patient_different_subscriber(self):
        """
        Testa que é possível criar pacientes com o mesmo CPF para assinantes diferentes.
        """
        # Criar o primeiro paciente
        self.use_case.execute(self.patient_data, self.subscriber_id)
        
        # Criar um segundo paciente com o mesmo CPF, mas para outro assinante
        another_subscriber_id = uuid.uuid4()
        
        # Isso não deve lançar exceção
        patient2 = self.use_case.execute(self.patient_data, another_subscriber_id)
        
        # Verificar que foi criado corretamente
        assert patient2 is not None
        assert patient2.subscriber_id == another_subscriber_id