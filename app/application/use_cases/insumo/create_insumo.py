"""
Caso de uso para criar um novo insumo.
"""

from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class CreateInsumoUseCase:
    """
    Caso de uso para criar um novo insumo no sistema.
    
    Implementa a lógica de negócio para criar um novo insumo,
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
                valor_unitario: Decimal,
                unidade_medida: str,
                estoque_minimo: int,
                estoque_atual: int,
                subscriber_id: UUID,
                fornecedor: Optional[str] = None,
                codigo_referencia: Optional[str] = None,
                data_validade: Optional[str] = None,
                data_compra: Optional[str] = None,
                observacoes: Optional[str] = None,
                modules_used: Optional[List[UUID]] = None) -> InsumoEntity:
        """
        Executa o caso de uso de criação de insumo.
        
        Args:
            nome: Nome do insumo
            descricao: Descrição detalhada do insumo
            categoria: Categoria do insumo (ex: MEDICAMENTO, EQUIPAMENTO)
            valor_unitario: Valor unitário do insumo
            unidade_medida: Unidade de medida (UN, CX, ML, KG)
            estoque_minimo: Quantidade mínima recomendada em estoque
            estoque_atual: Quantidade atual em estoque
            subscriber_id: ID do assinante ao qual o insumo pertence
            fornecedor: Nome do fornecedor (opcional)
            codigo_referencia: Código de referência ou SKU (opcional)
            data_validade: Data de validade do insumo (opcional)
            data_compra: Data da última compra (opcional)
            observacoes: Observações adicionais (opcional)
            modules_used: IDs dos módulos onde este insumo é usado (opcional)
            
        Returns:
            InsumoEntity: Entidade de insumo criada
        """
        # Criar a entidade de domínio
        insumo = InsumoEntity(
            nome=nome,
            descricao=descricao,
            categoria=categoria.upper(),
            valor_unitario=valor_unitario,
            unidade_medida=unidade_medida.upper(),
            estoque_minimo=estoque_minimo,
            estoque_atual=estoque_atual,
            subscriber_id=subscriber_id,
            fornecedor=fornecedor,
            codigo_referencia=codigo_referencia,
            data_validade=data_validade,
            data_compra=data_compra,
            observacoes=observacoes,
            modules_used=modules_used or []
        )
        
        # Salvar no repositório
        return self.insumo_repository.create(insumo)