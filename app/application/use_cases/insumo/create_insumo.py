"""
Caso de uso para criação de insumo.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class CreateInsumoUseCase:
    """
    Caso de uso para criação de um novo insumo.
    
    Implementa a lógica de negócio para criar um insumo,
    sem depender de detalhes específicos de banco de dados ou framework.
    """
    
    def __init__(self, insumo_repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com o repositório de insumos.
        
        Args:
            insumo_repository: Repositório de insumos que segue a interface definida
        """
        self.insumo_repository = insumo_repository
    
    def execute(self,
                nome: str,
                descricao: str,
                categoria: str,
                valor_unitario: float,
                unidade_medida: str,
                estoque_minimo: int,
                estoque_atual: int,
                subscriber_id: UUID,
                fornecedor: Optional[str] = None,
                codigo_referencia: Optional[str] = None,
                data_validade: Optional[str] = None,
                data_compra: Optional[str] = None,
                observacoes: Optional[str] = None,
                modules_used: Optional[List[Dict[str, Any]]] = None) -> InsumoEntity:
        """
        Executa o caso de uso de criação de insumo.
        
        Args:
            nome: Nome do insumo
            descricao: Descrição detalhada
            categoria: Categoria do insumo
            valor_unitario: Valor unitário
            unidade_medida: Unidade de medida
            estoque_minimo: Estoque mínimo recomendado
            estoque_atual: Estoque atual
            subscriber_id: ID do assinante proprietário
            fornecedor: Nome do fornecedor (opcional)
            codigo_referencia: Código de referência (opcional)
            data_validade: Data de validade (opcional)
            data_compra: Data de compra (opcional)
            observacoes: Observações adicionais (opcional)
            modules_used: Lista de módulos que usam este insumo (opcional)
            
        Returns:
            InsumoEntity: Entidade de insumo criada
        
        Raises:
            ValueError: Se os dados forem inválidos
        """
        # Validações básicas
        if valor_unitario <= 0:
            raise ValueError("Valor unitário deve ser maior que zero")
        
        if estoque_minimo < 0:
            raise ValueError("Estoque mínimo não pode ser negativo")
        
        if estoque_atual < 0:
            raise ValueError("Estoque atual não pode ser negativo")
        
        # Criar insumo no repositório
        insumo = self.insumo_repository.create(
            nome=nome,
            descricao=descricao,
            categoria=categoria,
            valor_unitario=valor_unitario,
            unidade_medida=unidade_medida,
            estoque_minimo=estoque_minimo,
            estoque_atual=estoque_atual,
            subscriber_id=subscriber_id,
            fornecedor=fornecedor,
            codigo_referencia=codigo_referencia,
            data_validade=data_validade,
            data_compra=data_compra,
            observacoes=observacoes,
            modules_used=modules_used
        )
        
        return insumo