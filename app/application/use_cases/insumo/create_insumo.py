"""
Caso de uso para criar um novo insumo.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface
from app.domain.insumo.value_objects.modulo_association import ModuloAssociation


class CreateInsumoUseCase:
    """
    Caso de uso para criar um novo insumo.
    
    Responsável por validar dados de entrada, criar uma nova entidade de insumo
    e persistir através do repositório.
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
            categoria: Categoria do insumo (ex: medicamento, material, etc)
            valor_unitario: Valor por unidade
            unidade_medida: Unidade de medida (ex: unidade, caixa, kg)
            estoque_minimo: Quantidade mínima recomendada
            estoque_atual: Quantidade atual em estoque
            subscriber_id: ID do assinante proprietário
            fornecedor: Nome do fornecedor
            codigo_referencia: Código de referência interno ou do fornecedor
            data_validade: Data de validade, se aplicável
            data_compra: Data da última compra
            observacoes: Observações adicionais
            modules_used: Lista de módulos associados com suas quantidades padrão
            
        Returns:
            InsumoEntity: Entidade de insumo criada
            
        Raises:
            ValueError: Se os dados fornecidos forem inválidos
        """
        # Validação básica
        if valor_unitario < 0:
            raise ValueError("Valor unitário não pode ser negativo")
            
        if estoque_minimo < 0:
            raise ValueError("Estoque mínimo não pode ser negativo")
            
        if estoque_atual < 0:
            raise ValueError("Estoque atual não pode ser negativo")
            
        # Processar associações de módulos
        module_associations = []
        if modules_used:
            for module_data in modules_used:
                module_id = module_data.get("module_id")
                if not module_id:
                    continue
                    
                try:
                    if isinstance(module_id, str):
                        module_id = UUID(module_id)
                        
                    module_associations.append(ModuloAssociation(
                        module_id=module_id,
                        quantidade_padrao=module_data.get("quantidade_padrao", 1),
                        observacao=module_data.get("observacao"),
                        module_nome=module_data.get("module_nome")
                    ))
                except (ValueError, TypeError):
                    # Ignorar associação inválida
                    continue
        
        # Criar entidade
        insumo = InsumoEntity(
            id=uuid4(),
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
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            modules_used=module_associations
        )
        
        # Persistir no repositório
        return self.repository.create(insumo)