"""
Entidades de domínio para o módulo de Insumos.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from app.domain.insumo.value_objects.modulo_association import ModuloAssociation


class InsumoEntity:
    """
    Entidade de domínio que representa um insumo.
    
    Um insumo é um item que compõe o estoque de suprimentos do estabelecimento,
    como materiais de consumo, medicamentos, produtos, etc.
    """
    
    def __init__(
        self,
        nome: str,
        descricao: str,
        categoria: str,
        valor_unitario: float,
        unidade_medida: str,
        estoque_minimo: int,
        estoque_atual: int,
        subscriber_id: UUID,
        id: Optional[UUID] = None,
        fornecedor: Optional[str] = None,
        codigo_referencia: Optional[str] = None,
        data_validade: Optional[str] = None, 
        data_compra: Optional[str] = None,
        observacoes: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        modules_used: Optional[List[ModuloAssociation]] = None
    ):
        """
        Inicializa um novo insumo.
        
        Args:
            nome: Nome do insumo
            descricao: Descrição detalhada
            categoria: Categoria do insumo (ex: medicamento, material, etc)
            valor_unitario: Valor por unidade
            unidade_medida: Unidade de medida (ex: unidade, caixa, kg)
            estoque_minimo: Quantidade mínima recomendada
            estoque_atual: Quantidade atual em estoque
            subscriber_id: ID do assinante proprietário
            id: ID único do insumo (gerado se não fornecido)
            fornecedor: Nome do fornecedor
            codigo_referencia: Código de referência interno ou do fornecedor
            data_validade: Data de validade, se aplicável
            data_compra: Data da última compra
            observacoes: Observações adicionais
            is_active: Se o insumo está ativo
            created_at: Data de criação
            updated_at: Data da última atualização
            modules_used: Lista de módulos que utilizam este insumo
        """
        # Valores obrigatórios
        self.id = id or uuid4()
        self.nome = nome
        self.descricao = descricao
        self.categoria = categoria
        self.valor_unitario = valor_unitario
        self.unidade_medida = unidade_medida
        self.estoque_minimo = estoque_minimo
        self.estoque_atual = estoque_atual
        self.subscriber_id = subscriber_id
        
        # Valores opcionais
        self.fornecedor = fornecedor
        self.codigo_referencia = codigo_referencia
        self.data_validade = data_validade
        self.data_compra = data_compra
        self.observacoes = observacoes
        self.is_active = is_active
        
        # Metadados
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        # Associações
        self.modules_used = modules_used or []
    
    def verificar_estoque_baixo(self) -> bool:
        """
        Verifica se o estoque está abaixo do mínimo.
        
        Returns:
            bool: True se o estoque atual for menor que o mínimo
        """
        return self.estoque_atual < self.estoque_minimo
    
    def calcular_valor_total(self) -> float:
        """
        Calcula o valor total do estoque atual.
        
        Returns:
            float: Valor total (estoque_atual * valor_unitario)
        """
        return self.estoque_atual * self.valor_unitario
    
    def adicionar_estoque(self, quantidade: int) -> None:
        """
        Adiciona quantidade ao estoque atual.
        
        Args:
            quantidade: Quantidade a adicionar
            
        Raises:
            ValueError: Se a quantidade for negativa ou zero
        """
        if quantidade <= 0:
            raise ValueError("Quantidade para adicionar deve ser maior que zero")
            
        self.estoque_atual += quantidade
        self.updated_at = datetime.utcnow()
    
    def reduzir_estoque(self, quantidade: int) -> None:
        """
        Reduz quantidade do estoque atual.
        
        Args:
            quantidade: Quantidade a reduzir
            
        Raises:
            ValueError: Se a quantidade for negativa, zero ou maior que o estoque atual
        """
        if quantidade <= 0:
            raise ValueError("Quantidade para reduzir deve ser maior que zero")
            
        if quantidade > self.estoque_atual:
            raise ValueError(f"Estoque insuficiente: atual {self.estoque_atual}, solicitado {quantidade}")
            
        self.estoque_atual -= quantidade
        self.updated_at = datetime.utcnow()
    
    def atualizar(self, **kwargs) -> None:
        """
        Atualiza atributos do insumo.
        
        Args:
            **kwargs: Dicionário de atributos e valores a atualizar
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_at', 'subscriber_id']:
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()