"""
Testes unitários para o caso de uso DeletePatientUseCase.
"""
import uuid
from datetime import date

import pytest
from fastapi import HTTPException

from app.application.use_cases.patient.delete_patient import DeletePatientUseCase
from app.tests.fakes.fake_patient_repository import FakePatientRepository
from app.domain.patient.entities import PatientEntity


class TestDeletePatientUseCase:
    """
    Testes para o caso de uso de exclusão lógica de paciente.
    """
    
    def setup_method(self):
        """
        Configuração antes de cada teste.
        """
        # Inicializar o repositório fake
        self.repository = FakePatientRepository()
        
        # Inicializar o caso de uso com o repositório fake
        self.use_case = DeletePatientUseCase(self.repository)
        
        # IDs para uso nos testes
        self.subscriber_id = uuid.uuid4()
        self.patient_id = uuid.uuid4()
        
        # Adicionar um paciente para testes
        self.test_patient = PatientEntity(
            id=self.patient_id,
            name="Teste da Silva",
            cpf="123.456.789-00",
            birth_date=date(1980, 1, 1),
            subscriber_id=self.subscriber_id,
            is_active=True
        )
        
        # Adicionar diretamente ao repositório
        self.repository.patients[self.patient_id] = self.test_patient
    
    def test_delete_patient_success(self):
        """
        Testa a exclusão lógica bem-sucedida de um paciente.
        """
        # Executar o caso de uso
        result = self.use_case.execute(self.patient_id, self.subscriber_id)
        
        # Verificar se a operação foi bem-sucedida
        assert result is True
        
        # Verificar se o paciente foi desativado no repositório
        patient = self.repository.patients[self.patient_id]
        assert patient.is_active is False
        
    def test_delete_nonexistent_patient(self):
        """
        Testa a tentativa de excluir um paciente inexistente.
        """
        # ID que não existe no repositório
        nonexistent_id = uuid.uuid4()
        
        # Verificar que uma exceção é lançada
        with pytest.raises(HTTPException) as excinfo:
            self.use_case.execute(nonexistent_id, self.subscriber_id)
        
        # Verificar o código de status
        assert excinfo.value.status_code == 404
        assert f"Paciente com ID {nonexistent_id} não encontrado" in excinfo.value.detail
    
    def test_delete_wrong_subscriber(self):
        """
        Testa a tentativa de excluir um paciente de outro assinante.
        """
        # ID de assinante diferente
        other_subscriber_id = uuid.uuid4()
        
        # Verificar que uma exceção é lançada
        with pytest.raises(HTTPException) as excinfo:
            self.use_case.execute(self.patient_id, other_subscriber_id)
        
        # Verificar o código de status
        assert excinfo.value.status_code == 404
        
    def test_delete_already_deleted_patient(self):
        """
        Testa a exclusão de um paciente que já estava desativado.
        """
        # Primeiro, desativa o paciente
        self.test_patient.is_active = False
        
        # Tenta desativar o paciente novamente
        result = self.use_case.execute(self.patient_id, self.subscriber_id)
        
        # A operação deve ser bem-sucedida (idempotente)
        assert result is True
        assert self.repository.patients[self.patient_id].is_active is False