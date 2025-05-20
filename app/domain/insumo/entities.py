"""
Entidades do domínio de insumos.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class InsumoEntity:
    """
    Entidade principal de insumo.
    """
    
    def __init__(
        self,
        subscriber_id: Optional[UUID] = None,
        nome: str = "",
        tipo: str = "",
        unidade: str = "",
        categoria: str = "",
        quantidade: float = 0.0,
        observacoes: Optional[str] = None,
        modulo_id: Optional[UUID] = None,
        id: Optional[UUID] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Inicializa uma nova entidade de insumo.
        
        Args:
            subscriber_id: ID do assinante proprietário
            nome: Nome do insumo
            tipo: Tipo do insumo (ex: medicamento, material, equipamento)
            unidade: Unidade de medida (ex: unidade, caixa, ml, kg)
            categoria: Categoria do insumo (ex: cirúrgico, hospitalar, administrativo)
            quantidade: Quantidade disponível (padrão: 0.0)
            observacoes: Observações adicionais (opcional)
            modulo_id: ID do módulo relacionado (opcional)
            id: ID único do insumo (gerado automaticamente se não for fornecido)
            is_active: Indica se o insumo está ativo
            created_at: Data de criação
            updated_at: Data da última atualização
        """
        self.id = id
        self.subscriber_id = subscriber_id
        self.nome = nome
        self.tipo = tipo
        self.unidade = unidade
        self.quantidade = quantidade
        self.categoria = categoria
        self.modulo_id = modulo_id
        self.observacoes = observacoes
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        # Validar campos obrigatórios
        self._validate()
    
    def _validate(self) -> None:
        """
        Valida os campos da entidade.
        
        Raises:
            ValueError: Se algum campo obrigatório estiver vazio ou inválido
        """
        if not self.nome or len(self.nome.strip()) == 0:
            raise ValueError("Nome do insumo é obrigatório")
        
        if not self.tipo or len(self.tipo.strip()) == 0:
            raise ValueError("Tipo do insumo é obrigatório")
        
        if not self.unidade or len(self.unidade.strip()) == 0:
            raise ValueError("Unidade de medida é obrigatória")
        
        if not self.categoria or len(self.categoria.strip()) == 0:
            raise ValueError("Categoria do insumo é obrigatória")
        
        if self.quantidade < 0:
            raise ValueError("Quantidade não pode ser negativa")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a entidade para um dicionário.
        
        Returns:
            Dict[str, Any]: Representação da entidade em dicionário
        """
        return {
            "id": self.id,
            "subscriber_id": self.subscriber_id,
            "nome": self.nome,
            "tipo": self.tipo,
            "unidade": self.unidade,
            "quantidade": self.quantidade,
            "categoria": self.categoria,
            "modulo_id": self.modulo_id,
            "observacoes": self.observacoes,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InsumoEntity":
        """
        Cria uma instância da entidade a partir de um dicionário.
        
        Args:
            data: Dicionário com os dados da entidade
            
        Returns:
            InsumoEntity: Nova instância da entidade
        """
        return cls(
            id=data.get("id"),
            subscriber_id=data["subscriber_id"],
            nome=data["nome"],
            tipo=data["tipo"],
            unidade=data["unidade"],
            quantidade=data.get("quantidade", 0.0),
            categoria=data["categoria"],
            modulo_id=data.get("modulo_id"),
            observacoes=data.get("observacoes"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )