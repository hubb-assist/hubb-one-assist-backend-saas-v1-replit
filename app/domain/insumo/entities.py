"""
Entidades de domínio para o módulo de Insumos.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID, uuid4


@dataclass
class InsumoEntity:
    """
    Entidade de domínio que representa um insumo no sistema.
    """
    nome: str
    tipo: str
    unidade: str
    categoria: str
    quantidade: float
    subscriber_id: UUID
    observacoes: Optional[str] = None
    modulo_id: Optional[UUID] = None
    is_active: bool = True
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        # Gerar ID se não for fornecido
        if self.id is None:
            self.id = uuid4()
        
        # Definir timestamps se não fornecidos
        now = datetime.utcnow()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def deactivate(self) -> None:
        """
        Desativa o insumo (exclusão lógica).
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a entidade para um dicionário.
        
        Returns:
            Dict[str, Any]: Dicionário com os atributos da entidade
        """
        return {
            "id": str(self.id) if self.id else None,
            "subscriber_id": str(self.subscriber_id) if self.subscriber_id else None,
            "nome": self.nome,
            "tipo": self.tipo,
            "unidade": self.unidade,
            "quantidade": self.quantidade,
            "categoria": self.categoria,
            "modulo_id": str(self.modulo_id) if self.modulo_id else None,
            "observacoes": self.observacoes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }