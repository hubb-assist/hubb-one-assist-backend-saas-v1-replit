"""
Testes unitários para o caso de uso ListSubscribersUseCase.
"""
import uuid

from app.application.use_cases.subscriber.list_subscribers import ListSubscribersUseCase
from app.tests.fakes.fake_subscriber_repository import FakeSubscriberRepository
from app.domain.subscriber.entities import SubscriberEntity


class TestListSubscribersUseCase:
    """
    Testes para o caso de uso de listagem de assinantes.
    """
    
    def setup_method(self):
        """
        Configuração antes de cada teste.
        """
        # Inicializar o repositório fake
        self.repository = FakeSubscriberRepository()
        
        # Inicializar o caso de uso com o repositório fake
        self.use_case = ListSubscribersUseCase(self.repository)
        
        # IDs para uso nos testes
        self.segment_id = uuid.uuid4()
        self.other_segment_id = uuid.uuid4()
        
        # Adicionar assinantes para testes
        self.subscribers = []
        
        # Assinante 1 - Segmento 1
        subscriber1 = SubscriberEntity(
            id=uuid.uuid4(),
            name="Empresa A",
            fantasy_name="A Corp",
            cnpj="12.345.678/0001-90",
            segment_id=self.segment_id,
            is_active=True
        )
        self.repository.subscribers[subscriber1.id] = subscriber1
        self.subscribers.append(subscriber1)
        
        # Assinante 2 - Segmento 1
        subscriber2 = SubscriberEntity(
            id=uuid.uuid4(),
            name="Empresa B",
            fantasy_name="B Corp",
            cnpj="98.765.432/0001-10",
            segment_id=self.segment_id,
            is_active=True
        )
        self.repository.subscribers[subscriber2.id] = subscriber2
        self.subscribers.append(subscriber2)
        
        # Assinante 3 - Segmento 1 (inativo)
        subscriber3 = SubscriberEntity(
            id=uuid.uuid4(),
            name="Empresa C",
            fantasy_name="C Corp",
            cnpj="11.222.333/0001-44",
            segment_id=self.segment_id,
            is_active=False
        )
        self.repository.subscribers[subscriber3.id] = subscriber3
        self.subscribers.append(subscriber3)
        
        # Assinante 4 - Segmento 2
        subscriber4 = SubscriberEntity(
            id=uuid.uuid4(),
            name="Empresa D",
            fantasy_name="D Corp",
            cnpj="55.666.777/0001-88",
            segment_id=self.other_segment_id,
            is_active=True
        )
        self.repository.subscribers[subscriber4.id] = subscriber4
        self.subscribers.append(subscriber4)
    
    def test_list_all_subscribers(self):
        """
        Testa a listagem de todos os assinantes.
        """
        # Executar o caso de uso
        result = self.use_case.execute()
        
        # Verificar resultados gerais
        assert result["total"] == 4  # Todos os assinantes, inclusive inativos
        assert len(result["items"]) == 4
        assert result["page"] == 1
        assert result["size"] == 10  # Tamanho padrão
        
        # Verificar nomes dos assinantes retornados
        names = [s.name for s in result["items"]]
        assert "Empresa A" in names
        assert "Empresa B" in names
        assert "Empresa C" in names
        assert "Empresa D" in names
    
    def test_list_subscribers_with_pagination(self):
        """
        Testa a listagem de assinantes com paginação.
        """
        # Executar o caso de uso com paginação
        result = self.use_case.execute(skip=1, limit=2)
        
        # Verificar resultados
        assert result["total"] == 4  # Total não muda com paginação
        assert len(result["items"]) == 2  # Apenas dois assinantes por página
        assert result["page"] == 2  # Segunda página (skip=1, limit=2)
        assert result["size"] == 2
        assert result["pages"] == 2  # 4 assinantes / 2 por página = 2 páginas
    
    def test_list_subscribers_by_segment(self):
        """
        Testa a listagem de assinantes filtrados por segmento.
        """
        # Executar o caso de uso com filtro por segmento
        result = self.use_case.execute(segment_id=self.segment_id)
        
        # Verificar resultados
        assert result["total"] == 3  # 3 assinantes do segmento 1
        assert len(result["items"]) == 3
        
        # Verificar que todos os assinantes são do segmento correto
        segment_ids = [s.segment_id for s in result["items"]]
        assert all(sid == self.segment_id for sid in segment_ids)
        
        # Verificar que não retorna assinantes do outro segmento
        names = [s.name for s in result["items"]]
        assert "Empresa A" in names
        assert "Empresa B" in names
        assert "Empresa C" in names
        assert "Empresa D" not in names  # Segmento diferente
    
    def test_list_subscribers_by_name(self):
        """
        Testa a listagem de assinantes filtrados por nome.
        """
        # Executar o caso de uso com filtro por nome
        result = self.use_case.execute(name="Empresa A")
        
        # Verificar resultados
        assert result["total"] == 1
        assert len(result["items"]) == 1
        assert result["items"][0].name == "Empresa A"
    
    def test_list_subscribers_by_cnpj(self):
        """
        Testa a listagem de assinantes filtrados por CNPJ.
        """
        # Executar o caso de uso com filtro por parte do CNPJ
        result = self.use_case.execute(cnpj="987")  # Parte do CNPJ do assinante 2
        
        # Verificar resultados
        assert result["total"] == 1
        assert len(result["items"]) == 1
        assert result["items"][0].name == "Empresa B"
    
    def test_list_active_subscribers_only(self):
        """
        Testa a listagem de apenas assinantes ativos.
        """
        # Executar o caso de uso com filtro por status de ativação
        result = self.use_case.execute(is_active=True)
        
        # Verificar resultados
        assert result["total"] == 3  # 3 assinantes ativos
        assert len(result["items"]) == 3
        
        # Verificar que todos os assinantes retornados estão ativos
        statuses = [s.is_active for s in result["items"]]
        assert all(status for status in statuses)
        
        # Verificar que não retorna o assinante inativo
        names = [s.name for s in result["items"]]
        assert "Empresa A" in names
        assert "Empresa B" in names
        assert "Empresa C" not in names  # Inativo
        assert "Empresa D" in names