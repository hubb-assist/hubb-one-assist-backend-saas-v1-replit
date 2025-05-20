"""
Entidades de domínio para Insumos.
Implementa as regras de negócio e validações específicas para insumos.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID, uuid4


@dataclass
class InsumoEntity:
    """
    Entidade de domínio para Insumo.
    Representa um insumo ou material usado nos serviços.
    """
    nome: str
    descricao: str
    categoria: str  # Pode ser 'MEDICAMENTO', 'EQUIPAMENTO', 'MATERIAL', etc.
    valor_unitario: Decimal
    unidade_medida: str  # Ex: 'UN', 'CX', 'ML', 'KG'
    estoque_minimo: int
    estoque_atual: int
    subscriber_id: UUID
    id: UUID = field(default_factory=uuid4)
    fornecedor: Optional[str] = None
    codigo_referencia: Optional[str] = None
    data_validade: Optional[datetime] = None
    data_compra: Optional[datetime] = None
    observacoes: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    modules_used: List[UUID] = field(default_factory=list)  # IDs dos módulos onde este insumo é usado
    
    def atualizar_estoque(self, quantidade: int) -> int:
        """
        Atualiza o estoque atual do insumo.
        
        Args:
            quantidade: Quantidade a ser adicionada (positiva) ou removida (negativa)
            
        Returns:
            int: Novo estoque atual após a operação
        """
        self.estoque_atual += quantidade
        self.updated_at = datetime.utcnow()
        return self.estoque_atual
    
    def verificar_estoque_baixo(self) -> bool:
        """
        Verifica se o estoque está abaixo do mínimo.
        
        Returns:
            bool: True se o estoque atual estiver abaixo do mínimo
        """
        return self.estoque_atual < self.estoque_minimo
    
    def calcular_valor_total(self) -> Decimal:
        """
        Calcula o valor total do insumo em estoque.
        
        Returns:
            Decimal: Valor total (valor unitário * estoque atual)
        """
        return self.valor_unitario * Decimal(str(self.estoque_atual))
    
    def desativar(self) -> None:
        """
        Desativa o insumo (soft delete).
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def reativar(self) -> None:
        """
        Reativa um insumo previamente desativado.
        """
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def adicionar_modulo(self, module_id: UUID) -> None:
        """
        Associa o insumo a um módulo funcional.
        
        Args:
            module_id: ID do módulo a ser associado
        """
        if module_id not in self.modules_used:
            self.modules_used.append(module_id)
            self.updated_at = datetime.utcnow()
    
    def remover_modulo(self, module_id: UUID) -> bool:
        """
        Remove a associação do insumo com um módulo.
        
        Args:
            module_id: ID do módulo a ser removido
            
        Returns:
            bool: True se a remoção foi bem-sucedida, False se o módulo não estava associado
        """
        if module_id in self.modules_used:
            self.modules_used.remove(module_id)
            self.updated_at = datetime.utcnow()
            return True
        return False