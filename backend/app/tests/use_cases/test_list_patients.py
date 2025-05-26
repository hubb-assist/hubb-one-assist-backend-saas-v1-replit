"""
Testes unitários para o caso de uso ListPatientsUseCase.
"""
import uuid
from datetime import date

from app.application.use_cases.patient.list_patients import ListPatientsUseCase
from app.tests.fakes.fake_patient_repository import FakePatientRepository
from app.domain.patient.entities import PatientEntity


class TestListPatientsUseCase:
    """
    Testes para o caso de uso de listagem de pacientes.
    """
    
    def setup_method(self):
        """
        Configuração antes de cada teste.
        """
        # Inicializar o repositório fake
        self.repository = FakePatientRepository()
        
        # Inicializar o caso de uso com o repositório fake
        self.use_case = ListPatientsUseCase(self.repository)
        
        # IDs para uso nos testes
        self.subscriber_id = uuid.uuid4()
        self.other_subscriber_id = uuid.uuid4()
        
        # Adicionar pacientes para testes
        self.patients = []
        
        # Paciente 1 - Assinante 1
        patient1 = PatientEntity(
            id=uuid.uuid4(),
            name="João da Silva",
            cpf="123.456.789-00",
            birth_date=date(1980, 1, 1),
            phone="(11) 99999-8888",
            subscriber_id=self.subscriber_id,
            is_active=True
        )
        self.repository.patients[patient1.id] = patient1
        self.patients.append(patient1)
        
        # Paciente 2 - Assinante 1
        patient2 = PatientEntity(
            id=uuid.uuid4(),
            name="Maria Oliveira",
            cpf="987.654.321-00",
            birth_date=date(1990, 5, 5),
            phone="(11) 88888-7777",
            subscriber_id=self.subscriber_id,
            is_active=True
        )
        self.repository.patients[patient2.id] = patient2
        self.patients.append(patient2)
        
        # Paciente 3 - Assinante 1 (inativo)
        patient3 = PatientEntity(
            id=uuid.uuid4(),
            name="Carlos Santos",
            cpf="111.222.333-44",
            birth_date=date(1975, 10, 15),
            phone="(11) 77777-6666",
            subscriber_id=self.subscriber_id,
            is_active=False
        )
        self.repository.patients[patient3.id] = patient3
        self.patients.append(patient3)
        
        # Paciente 4 - Assinante 2
        patient4 = PatientEntity(
            id=uuid.uuid4(),
            name="Ana Pereira",
            cpf="555.666.777-88",
            birth_date=date(1985, 7, 7),
            phone="(21) 55555-4444",
            subscriber_id=self.other_subscriber_id,
            is_active=True
        )
        self.repository.patients[patient4.id] = patient4
        self.patients.append(patient4)
    
    def test_list_patients_all(self):
        """
        Testa a listagem de todos os pacientes de um assinante.
        """
        # Executar o caso de uso
        result = self.use_case.execute(self.subscriber_id)
        
        # Verificar resultados gerais
        assert result["total"] == 3  # 3 pacientes para o assinante (incluindo inativos)
        assert len(result["items"]) == 3
        assert result["page"] == 1
        assert result["size"] == 10  # Tamanho padrão
        
        # Verificar nomes dos pacientes retornados
        names = [p.name for p in result["items"]]
        assert "João da Silva" in names
        assert "Maria Oliveira" in names
        assert "Carlos Santos" in names
        
        # Verificar que pacientes de outro assinante não são retornados
        assert "Ana Pereira" not in names
    
    def test_list_patients_with_pagination(self):
        """
        Testa a listagem de pacientes com paginação.
        """
        # Executar o caso de uso com paginação
        result = self.use_case.execute(
            subscriber_id=self.subscriber_id,
            skip=1,
            limit=1
        )
        
        # Verificar resultados
        assert result["total"] == 3  # Total não muda com paginação
        assert len(result["items"]) == 1  # Apenas um paciente por página
        assert result["page"] == 2  # Segunda página (skip=1, limit=1)
        assert result["size"] == 1  # Tamanho da página
        assert result["pages"] == 3  # 3 pacientes / 1 por página = 3 páginas
    
    def test_list_patients_with_name_filter(self):
        """
        Testa a listagem de pacientes com filtro por nome.
        """
        # Executar o caso de uso com filtro por nome
        result = self.use_case.execute(
            subscriber_id=self.subscriber_id,
            name="joão"  # Deve funcionar com case insensitive
        )
        
        # Verificar resultados
        assert result["total"] == 1
        assert len(result["items"]) == 1
        assert result["items"][0].name == "João da Silva"
    
    def test_list_patients_with_cpf_filter(self):
        """
        Testa a listagem de pacientes com filtro por CPF.
        """
        # Executar o caso de uso com filtro por CPF
        result = self.use_case.execute(
            subscriber_id=self.subscriber_id,
            cpf="987"  # Parte do CPF do paciente 2
        )
        
        # Verificar resultados
        assert result["total"] == 1
        assert len(result["items"]) == 1
        assert result["items"][0].name == "Maria Oliveira"
    
    def test_list_patients_empty_result(self):
        """
        Testa a listagem de pacientes quando não há resultados.
        """
        # Usar um ID de assinante que não existe no repositório
        non_existent_subscriber_id = uuid.uuid4()
        
        # Executar o caso de uso
        result = self.use_case.execute(non_existent_subscriber_id)
        
        # Verificar resultados
        assert result["total"] == 0
        assert len(result["items"]) == 0
        assert result["page"] == 1
        assert result["size"] == 10