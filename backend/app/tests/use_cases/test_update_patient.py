"""
Testes unitários para o caso de uso UpdatePatientUseCase.
"""
import uuid
from datetime import date

import pytest
from fastapi import HTTPException

from app.application.use_cases.patient.update_patient import UpdatePatientUseCase
from app.tests.fakes.fake_patient_repository import FakePatientRepository
from app.domain.patient.entities import PatientEntity
from app.schemas.patient import PatientUpdate


class TestUpdatePatientUseCase:
    """
    Testes para o caso de uso de atualização de paciente.
    """
    
    def setup_method(self):
        """
        Configuração antes de cada teste.
        """
        # Inicializar o repositório fake
        self.repository = FakePatientRepository()
        
        # Inicializar o caso de uso com o repositório fake
        self.use_case = UpdatePatientUseCase(self.repository)
        
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
    
    def test_update_patient_success(self):
        """
        Testa a atualização bem-sucedida de um paciente.
        """
        # Dados para atualização
        update_data = PatientUpdate(
            name="Teste da Silva Atualizado",
            phone="(11) 98765-4321"
        )
        
        # Executar o caso de uso
        updated_patient = self.use_case.execute(
            self.patient_id, update_data, self.subscriber_id
        )
        
        # Verificar se o paciente foi atualizado corretamente
        assert updated_patient.name == "Teste da Silva Atualizado"
        assert updated_patient.phone == "(11) 98765-4321"
        assert updated_patient.cpf == "123.456.789-00"  # Não foi modificado
        
        # Verificar se o paciente do repositório também foi atualizado
        stored_patient = self.repository.patients[self.patient_id]
        assert stored_patient.name == "Teste da Silva Atualizado"
        assert stored_patient.phone == "(11) 98765-4321"
    
    def test_update_nonexistent_patient(self):
        """
        Testa a tentativa de atualizar um paciente inexistente.
        """
        # ID que não existe no repositório
        nonexistent_id = uuid.uuid4()
        
        # Dados para atualização
        update_data = PatientUpdate(name="Nome Atualizado")
        
        # Verificar que uma exceção é lançada
        with pytest.raises(HTTPException) as excinfo:
            self.use_case.execute(nonexistent_id, update_data, self.subscriber_id)
        
        # Verificar o código de status
        assert excinfo.value.status_code == 404
        assert f"Paciente com ID {nonexistent_id} não encontrado" in excinfo.value.detail
    
    def test_update_wrong_subscriber(self):
        """
        Testa a tentativa de atualizar um paciente de outro assinante.
        """
        # ID de assinante diferente
        other_subscriber_id = uuid.uuid4()
        
        # Dados para atualização
        update_data = PatientUpdate(name="Nome Atualizado")
        
        # Verificar que uma exceção é lançada
        with pytest.raises(HTTPException) as excinfo:
            self.use_case.execute(self.patient_id, update_data, other_subscriber_id)
        
        # Verificar o código de status
        assert excinfo.value.status_code == 404
        
    def test_update_duplicate_cpf(self):
        """
        Testa a tentativa de atualizar um paciente para um CPF já existente.
        """
        # Adicionar outro paciente com CPF diferente
        second_patient_id = uuid.uuid4()
        second_patient = PatientEntity(
            id=second_patient_id,
            name="Segundo Paciente",
            cpf="987.654.321-00",
            birth_date=date(1990, 5, 5),
            subscriber_id=self.subscriber_id,
            is_active=True
        )
        self.repository.patients[second_patient_id] = second_patient
        
        # Tentar atualizar o segundo paciente para o mesmo CPF do primeiro
        update_data = PatientUpdate(cpf="123.456.789-00")
        
        # Verificar que uma exceção é lançada
        with pytest.raises(HTTPException) as excinfo:
            self.use_case.execute(second_patient_id, update_data, self.subscriber_id)
        
        # Verificar o código de status e a mensagem
        assert excinfo.value.status_code == 400
        assert "Já existe um paciente ativo com o CPF" in excinfo.value.detail