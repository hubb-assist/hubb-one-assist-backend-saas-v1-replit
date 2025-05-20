"""
Caso de uso para atualizar um insumo existente.
"""

from typing import Optional, Dict, Any
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class UpdateInsumoUseCase:
    """
    Caso de uso para atualizar um insumo existente.
    
    Implementa a lógica de negócio para atualizar um insumo,
    sem depender de detalhes específicos de banco de dados ou framework.
    """
    
    def __init__(self, insumo_repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com o repositório de insumos.
        
        Args:
            insumo_repository: Repositório de insumos que segue a interface definida
        """
        self.insumo_repository = insumo_repository
    
    def execute(self, insumo_id: UUID, data: Dict[str, Any]) -> Optional[InsumoEntity]:
        """
        Executa o caso de uso de atualização de insumo.
        
        Args:
            insumo_id: UUID do insumo a ser atualizado
            data: Dicionário com os campos a serem atualizados
            
        Returns:
            Optional[InsumoEntity]: Entidade de insumo atualizada se encontrada, None caso contrário
        """
        # Verificar se o insumo existe
        insumo = self.insumo_repository.get_by_id(insumo_id)
        if not insumo:
            return None
        
        # Formatar valores quando necessário
        if 'categoria' in data and data['categoria']:
            data['categoria'] = data['categoria'].upper()
        
        if 'unidade_medida' in data and data['unidade_medida']:
            data['unidade_medida'] = data['unidade_medida'].upper()
        
        # Atualizar no repositório
        return self.insumo_repository.update(insumo_id, data)