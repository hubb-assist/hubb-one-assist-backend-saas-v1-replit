"""
Caso de uso para criação de insumos.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface
from app.domain.insumo.value_objects.modulo_association import ModuloAssociation


class CreateInsumoUseCase:
    """
    Caso de uso para criar um novo insumo.
    
    Orquestra a validação, criação e persistência de um novo insumo
    seguindo as regras de negócio definidas na entidade de domínio.
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            repository: Implementação do repositório de insumos
        """
        self.repository = repository
    
    def execute(
        self,
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
        modules_used: Optional[List[Dict[str, Any]]] = None
    ) -> InsumoEntity:
        """
        Executa o caso de uso para criar um novo insumo.
        
        Args:
            nome: Nome do insumo
            descricao: Descrição detalhada
            categoria: Categoria do insumo
            valor_unitario: Valor unitário (deve ser positivo)
            unidade_medida: Unidade de medida (ex: kg, unid)
            estoque_minimo: Quantidade mínima desejada em estoque
            estoque_atual: Quantidade atual em estoque
            subscriber_id: ID do assinante a que pertence o insumo
            fornecedor: Nome do fornecedor (opcional)
            codigo_referencia: Código interno ou do fornecedor (opcional)
            data_validade: Data de validade (opcional)
            data_compra: Data da última compra (opcional)
            observacoes: Anotações gerais (opcional)
            modules_used: Lista de associações com módulos (opcional)
            
        Returns:
            InsumoEntity: Entidade de insumo criada
            
        Raises:
            ValueError: Se algum dado for inválido
        """
        # Converter associações de módulos para objetos de valor, se fornecidos
        modulos = []
        if modules_used:
            for module_data in modules_used:
                module = ModuloAssociation(
                    module_id=module_data["module_id"],
                    quantidade_padrao=module_data.get("quantidade_padrao", 1),
                    observacao=module_data.get("observacao"),
                    module_nome=module_data.get("module_nome")
                )
                modulos.append(module)
        
        # Criar a entidade de domínio, que validará os dados de acordo com regras de negócio
        insumo = InsumoEntity(
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
            modules_used=modulos
        )
        
        # Persistir no repositório
        created_insumo = self.repository.create(insumo)
        
        return created_insumo