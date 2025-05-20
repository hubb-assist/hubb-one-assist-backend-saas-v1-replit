"""
Caso de uso para atualizar um insumo existente.
"""

from typing import Dict, Any, List, Optional
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
        # Primeiro, buscar o insumo existente
        insumo_existente = self.repository.get_by_id(insumo_id)
        if not insumo_existente:
            return None
            
        # Processar associações de módulos, se fornecidas
        if "modules_used" in data and data["modules_used"]:
            modulos = []
            for module_data in data["modules_used"]:
                module = ModuloAssociation(
                    module_id=module_data["module_id"],
                    quantidade_padrao=module_data.get("quantidade_padrao", 1),
                    observacao=module_data.get("observacao"),
                    module_nome=module_data.get("module_nome")
                )
                modulos.append(module)
            data["modules_used"] = modulos
        
        # Atualizar o insumo utilizando o repositório
        updated_insumo = self.repository.update(insumo_id, data)
        
        return updated_insumo