"""
Caso de uso para criar um novo insumo.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface
from app.domain.insumo.value_objects.modulo_association import ModuloAssociation


class CreateInsumoUseCase:
    """
    Caso de uso para criar um novo insumo.
    
    Responsável por validar os dados de entrada e criar um novo insumo
    no repositório, aplicando as regras de negócio necessárias.
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            repository: Implementação do repositório de insumos
        """
        self.repository = repository
    
    def execute(self, data: Dict[str, Any]) -> InsumoEntity:
        """
        Executa o caso de uso para criar um novo insumo.
        
        Args:
            data: Dicionário com os dados do insumo a ser criado
            
        Returns:
            InsumoEntity: A entidade criada, com ID gerado
            
        Raises:
            ValueError: Se os dados fornecidos forem inválidos
        """
        # Validar campos obrigatórios
        required_fields = ["nome", "descricao", "categoria", "valor_unitario", 
                          "unidade_medida", "estoque_minimo", "estoque_atual", 
                          "subscriber_id"]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"Campo obrigatório ausente: {field}")
        
        # Validar campos numéricos
        if data["valor_unitario"] < 0:
            raise ValueError("Valor unitário não pode ser negativo")
            
        if data["estoque_minimo"] < 0:
            raise ValueError("Estoque mínimo não pode ser negativo")
            
        if data["estoque_atual"] < 0:
            raise ValueError("Estoque atual não pode ser negativo")
            
        # Validar e converter subscriber_id
        try:
            if isinstance(data["subscriber_id"], str):
                data["subscriber_id"] = UUID(data["subscriber_id"])
        except ValueError:
            raise ValueError("Formato inválido para subscriber_id")
            
        # Processar datas, se presentes
        if "data_validade" in data and data["data_validade"]:
            if isinstance(data["data_validade"], str):
                try:
                    data["data_validade"] = datetime.fromisoformat(data["data_validade"])
                except ValueError:
                    raise ValueError("Formato de data inválido para data_validade")
                    
        if "data_compra" in data and data["data_compra"]:
            if isinstance(data["data_compra"], str):
                try:
                    data["data_compra"] = datetime.fromisoformat(data["data_compra"])
                except ValueError:
                    raise ValueError("Formato de data inválido para data_compra")
            
            # Validar data de compra
            if "data_compra" in data and data["data_compra"]:
                if data["data_compra"] > datetime.utcnow():
                    raise ValueError("Data de compra não pode ser futura")
        
        # Processar associações de módulos, se presentes
        if "modules_used" in data and data["modules_used"]:
            modules_list = data["modules_used"]
            module_associations = []
            
            for module_data in modules_list:
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
                    
            # Atualizar no dicionário
            data["modules_used"] = module_associations
        else:
            data["modules_used"] = []
        
        # Criar entidade
        entity = InsumoEntity(
            nome=data["nome"],
            descricao=data["descricao"],
            categoria=data["categoria"],
            valor_unitario=data["valor_unitario"],
            unidade_medida=data["unidade_medida"],
            estoque_minimo=data["estoque_minimo"],
            estoque_atual=data["estoque_atual"],
            subscriber_id=data["subscriber_id"],
            fornecedor=data.get("fornecedor"),
            codigo_referencia=data.get("codigo_referencia"),
            data_validade=data.get("data_validade"),
            data_compra=data.get("data_compra"),
            observacoes=data.get("observacoes"),
            modules_used=data.get("modules_used", [])
        )
        
        # Salvar no repositório
        return self.repository.create(entity)