"""
Entidades de domínio para insumos.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from app.domain.insumo.value_objects.modulo_association import ModuloAssociation


@dataclass
class InsumoEntity:
    """
    Entidade de domínio para Insumo.
    
    Representa um insumo no contexto do sistema, com todas as suas propriedades
    e regras de negócio encapsuladas, independente da persistência.
    """
    nome: str
    descricao: str
    categoria: str
    valor_unitario: float
    unidade_medida: str
    estoque_minimo: int
    estoque_atual: int
    subscriber_id: UUID
    id: UUID = field(default_factory=uuid4)
    fornecedor: Optional[str] = None
    codigo_referencia: Optional[str] = None
    data_validade: Optional[str] = None
    data_compra: Optional[str] = None
    observacoes: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    modules_used: List[ModuloAssociation] = field(default_factory=list)
    
    def __post_init__(self):
        """
        Validação após inicialização da entidade.
        """
        self._validate()
    
    def _validate(self):
        """
        Validar a entidade de insumo.
        """
        if not self.nome or len(self.nome.strip()) == 0:
            raise ValueError("Nome do insumo não pode ser vazio")
        
        if not self.descricao or len(self.descricao.strip()) == 0:
            raise ValueError("Descrição do insumo não pode ser vazia")
            
        if not self.categoria or len(self.categoria.strip()) == 0:
            raise ValueError("Categoria do insumo não pode ser vazia")
            
        if self.valor_unitario <= 0:
            raise ValueError("Valor unitário deve ser maior que zero")
            
        if not self.unidade_medida or len(self.unidade_medida.strip()) == 0:
            raise ValueError("Unidade de medida não pode ser vazia")
            
        if self.estoque_minimo < 0:
            raise ValueError("Estoque mínimo não pode ser negativo")
            
        if self.estoque_atual < 0:
            raise ValueError("Estoque atual não pode ser negativo")
    
    def verificar_estoque_baixo(self) -> bool:
        """
        Verifica se o estoque está abaixo do mínimo.
        
        Returns:
            bool: True se o estoque atual estiver abaixo do mínimo
        """
        return self.estoque_atual < self.estoque_minimo
    
    def calcular_valor_total(self) -> float:
        """
        Calcula o valor total do estoque deste insumo.
        
        Returns:
            float: Valor total do estoque (quantidade * valor unitário)
        """
        return self.estoque_atual * self.valor_unitario
    
    def adicionar_estoque(self, quantidade: int) -> None:
        """
        Adiciona quantidade ao estoque.
        
        Args:
            quantidade: Quantidade a adicionar (deve ser positiva)
            
        Raises:
            ValueError: Se a quantidade for inválida
        """
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        
        self.estoque_atual += quantidade
        self.updated_at = datetime.utcnow()
    
    def reduzir_estoque(self, quantidade: int) -> None:
        """
        Reduz quantidade do estoque.
        
        Args:
            quantidade: Quantidade a reduzir (deve ser positiva)
            
        Raises:
            ValueError: Se a quantidade for inválida ou maior que o estoque disponível
        """
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        
        if quantidade > self.estoque_atual:
            raise ValueError(f"Estoque insuficiente. Disponível: {self.estoque_atual}, Solicitado: {quantidade}")
        
        self.estoque_atual -= quantidade
        self.updated_at = datetime.utcnow()