"""
Entidades de domínio para Insumos.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class InsumoEntity:
    """
    Entidade de domínio para Insumo.
    """
    
    def __init__(
        self,
        nome: str,
        tipo: str,
        unidade: str,
        categoria: str,
        subscriber_id: UUID,
        quantidade: float = 0,
        observacoes: Optional[str] = None,
        modulo_id: Optional[UUID] = None,
        id: Optional[UUID] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Inicializa uma nova entidade de Insumo.
        
        Args:
            nome: Nome do insumo
            tipo: Tipo do insumo (medicamento, material, equipamento)
            unidade: Unidade de medida (ampola, caixa, unidade)
            categoria: Categoria do insumo
            subscriber_id: ID do assinante proprietário
            quantidade: Quantidade disponível
            observacoes: Observações adicionais
            modulo_id: ID do módulo ao qual o insumo pertence
            id: Identificador único (gerado automaticamente se None)
            is_active: Flag que indica se o insumo está ativo
            created_at: Data de criação
            updated_at: Data de atualização
        """
        self.id = id or uuid4()
        self.nome = nome
        self.tipo = tipo
        self.unidade = unidade
        self.categoria = categoria
        self.subscriber_id = subscriber_id
        self.quantidade = quantidade
        self.observacoes = observacoes
        self.modulo_id = modulo_id
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        self._validate()
    
    def _validate(self) -> None:
        """
        Valida os dados da entidade.
        
        Raises:
            ValueError: Se algum dos dados for inválido
        """
        if not self.nome:
            raise ValueError("Nome do insumo é obrigatório")
        
        if not self.tipo:
            raise ValueError("Tipo do insumo é obrigatório")
        
        if not self.unidade:
            raise ValueError("Unidade de medida do insumo é obrigatória")
        
        if not self.categoria:
            raise ValueError("Categoria do insumo é obrigatória")
        
        if self.quantidade < 0:
            raise ValueError("Quantidade não pode ser negativa")
        
        if not self.subscriber_id:
            raise ValueError("ID do assinante é obrigatório")
    
    def update_info(self, 
                    nome: Optional[str] = None, 
                    tipo: Optional[str] = None,
                    unidade: Optional[str] = None,
                    categoria: Optional[str] = None,
                    quantidade: Optional[float] = None,
                    observacoes: Optional[str] = None,
                    modulo_id: Optional[UUID] = None) -> None:
        """
        Atualiza as informações do insumo.
        
        Args:
            nome: Novo nome
            tipo: Novo tipo
            unidade: Nova unidade de medida
            categoria: Nova categoria
            quantidade: Nova quantidade
            observacoes: Novas observações
            modulo_id: Novo ID de módulo
        """
        if nome is not None:
            self.nome = nome
        
        if tipo is not None:
            self.tipo = tipo
        
        if unidade is not None:
            self.unidade = unidade
        
        if categoria is not None:
            self.categoria = categoria
        
        if quantidade is not None:
            self.quantidade = quantidade
        
        if observacoes is not None:
            self.observacoes = observacoes
        
        if modulo_id is not None:
            self.modulo_id = modulo_id
        
        self.updated_at = datetime.utcnow()
        self._validate()
    
    def deactivate(self) -> None:
        """
        Desativa o insumo (exclusão lógica).
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """
        Converte a entidade para um dicionário.
        
        Returns:
            dict: Representação da entidade como dicionário
        """
        return {
            "id": str(self.id),
            "nome": self.nome,
            "tipo": self.tipo,
            "unidade": self.unidade,
            "categoria": self.categoria,
            "subscriber_id": str(self.subscriber_id),
            "quantidade": self.quantidade,
            "observacoes": self.observacoes,
            "modulo_id": str(self.modulo_id) if self.modulo_id else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }