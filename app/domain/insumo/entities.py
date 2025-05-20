"""
Entidades de domínio para insumos no sistema HUBB ONE Assist.
Implementa a lógica de negócio relacionada a insumos independente da infraestrutura.
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional
from decimal import Decimal


class InsumoEntity:
    """
    Entidade rica que representa um insumo no sistema.
    Contém dados e comportamentos relacionados a insumos.
    """
    def __init__(
        self,
        id: Optional[UUID] = None,
        subscriber_id: Optional[UUID] = None,
        nome: str = "",
        tipo: str = "",
        unidade: str = "",
        valor: Decimal = Decimal("0.00"),
        observacoes: Optional[str] = None,
        categoria: str = "",
        modulos: Optional[List[str]] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or uuid4()
        self.subscriber_id = subscriber_id
        self.nome = nome.strip()
        self.tipo = tipo.strip()
        self.unidade = unidade.strip()
        self.valor = Decimal(str(valor))
        self.observacoes = observacoes.strip() if observacoes else None
        self.categoria = categoria.strip()
        self.modulos = modulos if modulos is not None else []
        
        # Relacionamento e auditoria
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def deactivate(self) -> None:
        """
        Desativa o insumo logicamente sem remover os dados.
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """
        Reativa um insumo previamente desativado.
        """
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def update_info(
        self,
        nome: Optional[str] = None,
        tipo: Optional[str] = None,
        unidade: Optional[str] = None,
        valor: Optional[Decimal] = None,
        observacoes: Optional[str] = None,
        categoria: Optional[str] = None,
        modulos: Optional[List[str]] = None
    ) -> None:
        """
        Atualiza informações do insumo.
        
        Args:
            nome: Novo nome
            tipo: Novo tipo
            unidade: Nova unidade
            valor: Novo valor
            observacoes: Novas observações
            categoria: Nova categoria
            modulos: Novos módulos
        """
        if nome is not None:
            self.nome = nome.strip()
        if tipo is not None:
            self.tipo = tipo.strip()
        if unidade is not None:
            self.unidade = unidade.strip()
        if valor is not None:
            self.valor = Decimal(str(valor))
        if observacoes is not None:
            self.observacoes = observacoes.strip() if observacoes else None
        if categoria is not None:
            self.categoria = categoria.strip()
        if modulos is not None:
            self.modulos = modulos
        
        self.updated_at = datetime.utcnow()
    
    def pertence_a_modulo(self, modulo: str) -> bool:
        """
        Verifica se o insumo pertence a um determinado módulo.
        
        Args:
            modulo: Nome do módulo a verificar
            
        Returns:
            bool: True se o insumo pertence ao módulo, False caso contrário
        """
        return modulo in self.modulos