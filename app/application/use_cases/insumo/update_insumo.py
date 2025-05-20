"""
Caso de uso para atualização de insumo.
"""

from typing import Optional, Dict, Any
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class UpdateInsumoUseCase:
    """
    Caso de uso para atualização de um insumo existente.
    
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
        Executa o caso de uso para atualizar um insumo.
        
        Args:
            insumo_id: UUID do insumo a atualizar
            data: Dicionário com os campos a serem atualizados
            
        Returns:
            Optional[InsumoEntity]: Entidade de insumo atualizada ou None se não encontrado
            
        Raises:
            ValueError: Se os dados de atualização forem inválidos
        """
        # Buscar insumo existente para verificar se existe
        insumo = self.insumo_repository.get_by_id(insumo_id)
        if not insumo:
            return None
            
        # Validar dados antes de atualizar
        if 'valor_unitario' in data and data['valor_unitario'] is not None:
            if float(data['valor_unitario']) <= 0:
                raise ValueError("Valor unitário deve ser maior que zero")
                
        if 'estoque_minimo' in data and data['estoque_minimo'] is not None:
            if int(data['estoque_minimo']) < 0:
                raise ValueError("Estoque mínimo não pode ser negativo")
                
        if 'estoque_atual' in data and data['estoque_atual'] is not None:
            if int(data['estoque_atual']) < 0:
                raise ValueError("Estoque atual não pode ser negativo")
                
        # Executar atualização no repositório
        insumo_atualizado = self.insumo_repository.update(insumo_id, data)
        
        return insumo_atualizado