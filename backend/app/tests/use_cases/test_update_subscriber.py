"""
Testes unitários para o caso de uso UpdateSubscriberUseCase.
"""
import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from app.application.use_cases.subscriber.update_subscriber import UpdateSubscriberUseCase
from app.tests.fakes.fake_subscriber_repository import FakeSubscriberRepository
from app.domain.subscriber.entities import SubscriberEntity
from app.schemas.subscriber import SubscriberUpdate


class TestUpdateSubscriberUseCase:
    """
    Testes para o caso de uso de atualização de assinante.
    """
    
    def setup_method(self):
        """
        Configuração antes de cada teste.
        """
        # Inicializar o repositório fake
        self.repository = FakeSubscriberRepository()
        
        # Inicializar o caso de uso com o repositório fake
        self.use_case = UpdateSubscriberUseCase(self.repository)
        
        # IDs para uso nos testes
        self.subscriber_id = uuid.uuid4()
        self.segment_id = uuid.uuid4()
        
        # Dados para o assinante de teste
        self.test_subscriber = SubscriberEntity(
            id=self.subscriber_id,
            name="Empresa Original",
            fantasy_name="Original Company",
            cnpj="12.345.678/0001-90",
            segment_id=self.segment_id,
            is_active=True
        )
        
        # Adicionar diretamente ao repositório
        self.repository.subscribers[self.subscriber_id] = self.test_subscriber
    
    def test_update_subscriber_success(self):
        """
        Testa a atualização bem-sucedida de um assinante.
        """
        # Dados para atualização
        new_name = "Empresa Atualizada"
        update_data = SubscriberUpdate(
            name=new_name,
            contact_email="novo@email.com"
        )
        
        # Executar o caso de uso
        updated_subscriber = self.use_case.execute(self.subscriber_id, update_data)
        
        # Verificar se o assinante foi atualizado corretamente
        assert updated_subscriber.name == new_name
        assert updated_subscriber.contact_email == "novo@email.com"
        assert updated_subscriber.fantasy_name == "Original Company"  # Não modificado
        assert updated_subscriber.cnpj == "12.345.678/0001-90"  # Não modificado
        
        # Verificar se o assinante no repositório também foi atualizado
        stored_subscriber = self.repository.subscribers[self.subscriber_id]
        assert stored_subscriber.name == new_name
        assert stored_subscriber.contact_email == "novo@email.com"
    
    def test_update_nonexistent_subscriber(self):
        """
        Testa a tentativa de atualizar um assinante inexistente.
        """
        # ID que não existe no repositório
        nonexistent_id = uuid.uuid4()
        
        # Dados para atualização
        update_data = SubscriberUpdate(name="Novo Nome")
        
        # Verificar que uma exceção é lançada
        with pytest.raises(HTTPException) as excinfo:
            self.use_case.execute(nonexistent_id, update_data)
        
        # Verificar o código de status
        assert excinfo.value.status_code == 404
        assert f"Assinante com ID {nonexistent_id} não encontrado" in excinfo.value.detail
    
    def test_update_duplicate_cnpj(self):
        """
        Testa a tentativa de atualizar um assinante para um CNPJ já existente.
        """
        # Adicionar outro assinante com CNPJ diferente
        second_subscriber_id = uuid.uuid4()
        second_subscriber = SubscriberEntity(
            id=second_subscriber_id,
            name="Segunda Empresa",
            cnpj="98.765.432/0001-10",
            is_active=True
        )
        self.repository.subscribers[second_subscriber_id] = second_subscriber
        
        # Tentar atualizar o segundo assinante para o mesmo CNPJ do primeiro
        update_data = SubscriberUpdate(cnpj="12.345.678/0001-90")
        
        # Verificar que uma exceção é lançada
        with pytest.raises(HTTPException) as excinfo:
            self.use_case.execute(second_subscriber_id, update_data)
        
        # Verificar o código de status e a mensagem
        assert excinfo.value.status_code == 400
        assert "Já existe um assinante ativo com o CNPJ" in excinfo.value.detail
    
    def test_update_multiple_fields(self):
        """
        Testa a atualização de múltiplos campos de um assinante.
        """
        # Data futura para active_until
        active_until = datetime.utcnow() + timedelta(days=365)
        new_segment_id = uuid.uuid4()
        
        # Dados para atualização
        update_data = SubscriberUpdate(
            name="Nome Completo Atualizado",
            fantasy_name="Novo Nome Fantasia",
            contact_phone="(11) 98765-4321",
            active_until=active_until,
            segment_id=str(new_segment_id),
            is_active=True
        )
        
        # Executar o caso de uso
        updated_subscriber = self.use_case.execute(self.subscriber_id, update_data)
        
        # Verificar se todos os campos foram atualizados corretamente
        assert updated_subscriber.name == "Nome Completo Atualizado"
        assert updated_subscriber.fantasy_name == "Novo Nome Fantasia"
        assert updated_subscriber.contact_phone == "(11) 98765-4321"
        assert updated_subscriber.active_until == active_until
        assert updated_subscriber.segment_id == new_segment_id
        assert updated_subscriber.is_active is True