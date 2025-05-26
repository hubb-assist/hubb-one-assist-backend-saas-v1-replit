"""
Testes unitários para o caso de uso DeleteSubscriberUseCase.
"""
import uuid

import pytest
from fastapi import HTTPException

from app.application.use_cases.subscriber.delete_subscriber import DeleteSubscriberUseCase
from app.tests.fakes.fake_subscriber_repository import FakeSubscriberRepository
from app.domain.subscriber.entities import SubscriberEntity


class TestDeleteSubscriberUseCase:
    """
    Testes para o caso de uso de exclusão lógica (desativação) de assinante.
    """
    
    def setup_method(self):
        """
        Configuração antes de cada teste.
        """
        # Inicializar o repositório fake
        self.repository = FakeSubscriberRepository()
        
        # Inicializar o caso de uso com o repositório fake
        self.use_case = DeleteSubscriberUseCase(self.repository)
        
        # IDs para uso nos testes
        self.subscriber_id = uuid.uuid4()
        
        # Adicionar um assinante para testes
        self.test_subscriber = SubscriberEntity(
            id=self.subscriber_id,
            name="Empresa Teste",
            is_active=True
        )
        
        # Adicionar diretamente ao repositório
        self.repository.subscribers[self.subscriber_id] = self.test_subscriber
    
    def test_delete_subscriber_success(self):
        """
        Testa a desativação bem-sucedida de um assinante.
        """
        # Executar o caso de uso
        result = self.use_case.execute(self.subscriber_id)
        
        # Verificar o resultado da operação
        assert result is True
        
        # Verificar se o assinante foi desativado no repositório
        subscriber = self.repository.subscribers[self.subscriber_id]
        assert subscriber.is_active is False
    
    def test_delete_nonexistent_subscriber(self):
        """
        Testa a tentativa de desativar um assinante inexistente.
        """
        # ID que não existe no repositório
        nonexistent_id = uuid.uuid4()
        
        # Verificar que uma exceção é lançada
        with pytest.raises(HTTPException) as excinfo:
            self.use_case.execute(nonexistent_id)
        
        # Verificar o código de status e a mensagem
        assert excinfo.value.status_code == 404
        assert f"Assinante com ID {nonexistent_id} não encontrado" in excinfo.value.detail
    
    def test_delete_already_inactive_subscriber(self):
        """
        Testa a desativação de um assinante que já estava inativo.
        """
        # Primeiro, desativa o assinante
        self.test_subscriber.is_active = False
        
        # Executar o caso de uso
        result = self.use_case.execute(self.subscriber_id)
        
        # A operação deve ser bem-sucedida (idempotente)
        assert result is True
        assert self.repository.subscribers[self.subscriber_id].is_active is False