"""
Caso de uso para criar um novo insumo.
"""
from typing import Optional, Dict, Any
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class CreateInsumoUseCase:
    """
    Caso de uso para criar um novo insumo.
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso.
        
        Args:
            repository: Repositório de insumos
        """
        self.repository = repository
    
    def execute(
        self,
        subscriber_id: UUID,
        nome: str,
        tipo: str,
        unidade: str,
        categoria: str,
        quantidade: float = 0.0,
        observacoes: Optional[str] = None,
        modulo_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Executa o caso de uso para criar um novo insumo.
        
        Args:
            subscriber_id: ID do assinante proprietário
            nome: Nome do insumo
            tipo: Tipo do insumo (ex: medicamento, material, equipamento)
            unidade: Unidade de medida (ex: unidade, caixa, ml, kg)
            categoria: Categoria do insumo (ex: cirúrgico, hospitalar, administrativo)
            quantidade: Quantidade disponível (padrão: 0.0)
            observacoes: Observações adicionais (opcional)
            modulo_id: ID do módulo relacionado (opcional)
            
        Returns:
            Dict[str, Any]: Dados do insumo criado
            
        Raises:
            ValueError: Se os dados forem inválidos
        """
        # Criar entidade
        entity = InsumoEntity(
            subscriber_id=subscriber_id,
            nome=nome,
            tipo=tipo,
            unidade=unidade,
            categoria=categoria,
            quantidade=quantidade,
            observacoes=observacoes,
            modulo_id=modulo_id
        )
        
        # Persistir no repositório
        result = self.repository.create(entity)
        
        # Retornar como dicionário
        return result.to_dict()