"""
Caso de uso para atualizar um insumo existente.
"""

from typing import Dict, Any, Optional, List
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface
from app.domain.insumo.value_objects.modulo_association import ModuloAssociation


class UpdateInsumoUseCase:
    """
    Caso de uso para atualizar um insumo existente.
    
    Permite modificar os atributos de um insumo existente,
    mantendo a integridade dos dados e regras de negócio.
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            repository: Implementação do repositório de insumos
        """
        self.repository = repository
    
    def execute(self, insumo_id: UUID, data: Dict[str, Any]) -> Optional[InsumoEntity]:
        """
        Executa o caso de uso para atualizar um insumo existente.
        
        Args:
            insumo_id: ID do insumo a ser atualizado
            data: Dicionário com os campos a serem atualizados
            
        Returns:
            Optional[InsumoEntity]: Entidade atualizada ou None se não encontrada
            
        Raises:
            ValueError: Se os dados fornecidos forem inválidos
        """
        # Validações básicas para campos numéricos
        if "valor_unitario" in data and data["valor_unitario"] is not None:
            if data["valor_unitario"] < 0:
                raise ValueError("Valor unitário não pode ser negativo")
                
        if "estoque_minimo" in data and data["estoque_minimo"] is not None:
            if data["estoque_minimo"] < 0:
                raise ValueError("Estoque mínimo não pode ser negativo")
                
        if "estoque_atual" in data and data["estoque_atual"] is not None:
            if data["estoque_atual"] < 0:
                raise ValueError("Estoque atual não pode ser negativo")
        
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
        
        # Enviar para o repositório
        return self.repository.update(insumo_id, data)