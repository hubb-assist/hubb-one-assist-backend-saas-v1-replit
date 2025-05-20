"""
Entidades do domínio de Insumos.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.domain.insumo.value_objects.modulo_association import ModuloAssociation


@dataclass
class InsumoEntity:
    """
    Entidade rica de domínio para Insumos.
    Representa um insumo (material/suprimento) com suas informações 
    e comportamentos de negócio.
    """
    nome: str
    descricao: str
    categoria: str
    valor_unitario: float
    unidade_medida: str
    estoque_minimo: int
    estoque_atual: int
    subscriber_id: UUID
    id: UUID
    fornecedor: Optional[str] = None
    codigo_referencia: Optional[str] = None
    data_validade: Optional[datetime] = None
    data_compra: Optional[datetime] = None
    observacoes: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    modules_used: List[ModuloAssociation] = field(default_factory=list)
    
    def verificar_estoque_baixo(self) -> bool:
        """
        Verifica se o estoque está abaixo do mínimo recomendado.
        
        Returns:
            bool: True se o estoque estiver abaixo do mínimo, False caso contrário
        """
        return self.estoque_atual < self.estoque_minimo
    
    def calcular_valor_total(self) -> float:
        """
        Calcula o valor total do estoque.
        
        Returns:
            float: Valor total (estoque_atual * valor_unitário)
        """
        return self.estoque_atual * self.valor_unitario
    
    def adicionar_estoque(self, quantidade: int) -> None:
        """
        Adiciona quantidade ao estoque atual.
        
        Args:
            quantidade: Quantidade a ser adicionada (deve ser positiva)
        
        Raises:
            ValueError: Se a quantidade for negativa
        """
        if quantidade < 0:
            raise ValueError("Quantidade a ser adicionada deve ser positiva")
        
        self.estoque_atual += quantidade
        self.updated_at = datetime.utcnow()
    
    def remover_estoque(self, quantidade: int) -> None:
        """
        Remove quantidade do estoque atual.
        
        Args:
            quantidade: Quantidade a ser removida (deve ser positiva)
        
        Raises:
            ValueError: Se a quantidade for negativa ou maior que o estoque disponível
        """
        if quantidade < 0:
            raise ValueError("Quantidade a ser removida deve ser positiva")
        
        if quantidade > self.estoque_atual:
            raise ValueError(f"Estoque insuficiente. Disponível: {self.estoque_atual}, Solicitado: {quantidade}")
        
        self.estoque_atual -= quantidade
        self.updated_at = datetime.utcnow()
    
    def atualizar(self, data: Dict[str, Any]) -> None:
        """
        Atualiza os atributos da entidade com os dados fornecidos.
        
        Args:
            data: Dicionário contendo os campos a serem atualizados
        """
        if 'nome' in data and data['nome']:
            self.nome = data['nome']
        
        if 'descricao' in data and data['descricao'] is not None:
            self.descricao = data['descricao']
        
        if 'categoria' in data and data['categoria']:
            self.categoria = data['categoria']
        
        if 'valor_unitario' in data and data['valor_unitario'] is not None:
            self.valor_unitario = data['valor_unitario']
        
        if 'unidade_medida' in data and data['unidade_medida']:
            self.unidade_medida = data['unidade_medida']
        
        if 'estoque_minimo' in data and data['estoque_minimo'] is not None:
            self.estoque_minimo = data['estoque_minimo']
        
        if 'estoque_atual' in data and data['estoque_atual'] is not None:
            self.estoque_atual = data['estoque_atual']
        
        if 'fornecedor' in data:
            self.fornecedor = data['fornecedor']
        
        if 'codigo_referencia' in data:
            self.codigo_referencia = data['codigo_referencia']
        
        if 'data_validade' in data:
            self.data_validade = data['data_validade']
        
        if 'data_compra' in data:
            self.data_compra = data['data_compra']
        
        if 'observacoes' in data:
            self.observacoes = data['observacoes']
        
        if 'is_active' in data and data['is_active'] is not None:
            self.is_active = data['is_active']
        
        self.updated_at = datetime.utcnow()
    
    def desativar(self) -> None:
        """
        Desativa o insumo (soft delete).
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()