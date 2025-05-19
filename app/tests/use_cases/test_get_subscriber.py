"""
Testes unitários para o caso de uso GetSubscriberUseCase.
"""
import uuid

import pytest
from fastapi import HTTPException

from app.application.use_cases.subscriber.get_subscriber import GetSubscriberUseCase
from app.tests.fakes.fake_subscriber_repository import FakeSubscriberRepository
from app.domain.subscriber.entities import SubscriberEntity


class TestGetSubscriberUseCase:
    """
    Testes para o caso de uso de busca de assinante por ID.
    """
    
    def setup_method(self):
        """
        Configuração antes de cada teste.
        """
        # Inicializar o repositório fake
        self.repository = FakeSubscriberRepository()
        
        # Inicializar o caso de uso com o repositório fake
        self.use_case = GetSubscriberUseCase(self.repository)
        
        # IDs para uso nos testes
        self.subscriber_id = uuid.uuid4()
        self.segment_id = uuid.uuid4()
        
        # Adicionar um assinante para testes
        self.test_subscriber = SubscriberEntity(
            id=self.subscriber_id,
            name="Empresa Teste",
            fantasy_name="TestCorp",
            cnpj="12.345.678/0001-90",
            segment_id=self.segment_id,
            is_active=True
        )
        
        # Adicionar diretamente ao repositório
        self.repository.subscribers[self.subscriber_id] = self.test_subscriber
    
    def test_get_subscriber_success(self):
        """
        Testa a busca bem-sucedida de um assinante por ID.
        """
        # Executar o caso de uso
        subscriber = self.use_case.execute(self.subscriber_id)
        
        # Verificar se o assinante foi retornado corretamente
        assert subscriber is not None
        assert subscriber.id == self.subscriber_id
        assert subscriber.name == "Empresa Teste"
        assert subscriber.fantasy_name == "TestCorp"
        assert subscriber.cnpj == "12.345.678/0001-90"
        assert subscriber.segment_id == self.segment_id
        assert subscriber.is_active is True
    
    def test_get_nonexistent_subscriber(self):
        """
        Testa a tentativa de buscar um assinante inexistente.
        """
        # ID que não existe no repositório
        nonexistent_id = uuid.uuid4()
        
        # Verificar que uma exceção é lançada
        with pytest.raises(HTTPException) as excinfo:
            self.use_case.execute(nonexistent_id)
        
        # Verificar o código de status e a mensagem
        assert excinfo.value.status_code == 404
        assert f"Assinante com ID {nonexistent_id} não encontrado" in excinfo.value.detail