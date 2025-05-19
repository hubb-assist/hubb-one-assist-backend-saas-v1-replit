"""
Testes unitários para o caso de uso CreateSubscriberUseCase.
"""
import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from app.application.use_cases.subscriber.create_subscriber import CreateSubscriberUseCase
from app.tests.fakes.fake_subscriber_repository import FakeSubscriberRepository
from app.schemas.subscriber import SubscriberCreate


class TestCreateSubscriberUseCase:
    """
    Testes para o caso de uso de criação de assinante.
    """
    
    def setup_method(self):
        """
        Configuração antes de cada teste.
        """
        # Inicializar o repositório fake
        self.repository = FakeSubscriberRepository()
        
        # Inicializar o caso de uso com o repositório fake
        self.use_case = CreateSubscriberUseCase(self.repository)
    
    def test_create_subscriber_success(self):
        """
        Testa a criação bem-sucedida de um assinante.
        """
        # Preparar dados de criação válidos
        segment_id = uuid.uuid4()
        active_until = datetime.utcnow() + timedelta(days=365)
        
        # Criar um objeto SubscriberCreate
        subscriber_data = SubscriberCreate(
            name="Empresa Teste Ltda",
            fantasy_name="Teste Company",
            cnpj="12.345.678/0001-90",
            active_until=active_until,
            contact_email="contato@teste.com",
            contact_phone="(11) 98765-4321",
            segment_id=str(segment_id)
        )
        
        # Executar o caso de uso
        result = self.use_case.execute(subscriber_data, segment_id)
        
        # Verificar se o assinante foi criado corretamente
        assert result is not None
        assert result.name == "Empresa Teste Ltda"
        assert result.fantasy_name == "Teste Company"
        assert result.cnpj == "12.345.678/0001-90"
        assert result.active_until == active_until
        assert result.segment_id == segment_id
        assert result.is_active is True
        assert result.created_at is not None
        assert result.updated_at is not None
        
        # Verificar se o assinante foi adicionado ao repositório
        assert len(self.repository.subscribers) == 1
        assert result.id in self.repository.subscribers
    
    def test_create_subscriber_with_modules_and_plans(self):
        """
        Testa a criação de um assinante com módulos e planos.
        """
        # Criar IDs para módulos e planos
        module_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        plan_ids = [str(uuid.uuid4())]
        
        # Criar um objeto SubscriberCreate com módulos e planos
        subscriber_data = SubscriberCreate(
            name="Empresa Com Módulos e Planos",
            modules=module_ids,
            plans=plan_ids
        )
        
        # Executar o caso de uso
        result = self.use_case.execute(subscriber_data)
        
        # Verificar se os módulos e planos foram atribuídos corretamente
        assert len(result.modules) == 2
        assert len(result.plans) == 1
        assert str(result.modules[0]) == module_ids[0]
        assert str(result.modules[1]) == module_ids[1]
        assert str(result.plans[0]) == plan_ids[0]
    
    def test_create_subscriber_duplicate_cnpj(self):
        """
        Testa a tentativa de criar um assinante com CNPJ duplicado.
        """
        # Primeiro, criar um assinante com um CNPJ
        subscriber_data1 = SubscriberCreate(
            name="Empresa Original",
            cnpj="12.345.678/0001-90"
        )
        self.use_case.execute(subscriber_data1)
        
        # Agora, tentar criar outro assinante com o mesmo CNPJ
        subscriber_data2 = SubscriberCreate(
            name="Empresa Duplicada",
            cnpj="12.345.678/0001-90"
        )
        
        # Verificar que uma exceção é lançada
        with pytest.raises(HTTPException) as excinfo:
            self.use_case.execute(subscriber_data2)
        
        # Verificar o código de status e a mensagem
        assert excinfo.value.status_code == 400
        assert "Já existe um assinante ativo com o CNPJ" in excinfo.value.detail
        
        # Verificar que apenas o primeiro assinante foi adicionado ao repositório
        assert len(self.repository.subscribers) == 1