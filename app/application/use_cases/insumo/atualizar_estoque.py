"""
Caso de uso para atualizar o estoque de um insumo.
"""

from typing import Optional, Dict, Any, Tuple
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class AtualizarEstoqueInsumoUseCase:
    """
    Caso de uso para atualizar o estoque de um insumo.
    
    Implementa a lógica de negócio para adicionar ou remover
    quantidades do estoque de um insumo.
    """
    
    def __init__(self, insumo_repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com o repositório de insumos.
        
        Args:
            insumo_repository: Repositório de insumos que segue a interface definida
        """
        self.insumo_repository = insumo_repository
    
    def execute(self, 
                insumo_id: UUID, 
                quantidade: int,
                observacao: Optional[str] = None) -> Tuple[bool, Optional[InsumoEntity], str]:
        """
        Executa o caso de uso de atualização de estoque.
        
        Args:
            insumo_id: UUID do insumo a ser atualizado
            quantidade: Quantidade a adicionar (positiva) ou remover (negativa)
            observacao: Observação opcional sobre a movimentação
            
        Returns:
            Tuple[bool, Optional[InsumoEntity], str]: 
                - Sucesso da operação (bool)
                - Entidade atualizada (InsumoEntity ou None em caso de erro)
                - Mensagem de resultado ou erro
        """
        # Verificar se o insumo existe
        insumo = self.insumo_repository.get_by_id(insumo_id)
        if not insumo:
            return False, None, "Insumo não encontrado"
        
        # Verificar se a quantidade não levará o estoque para negativo
        novo_estoque = insumo.estoque_atual + quantidade
        if novo_estoque < 0:
            return False, None, f"Estoque insuficiente. Disponível: {insumo.estoque_atual}"
        
        # Atualizar o estoque
        data = {
            "estoque_atual": novo_estoque
        }
        
        # Se tiver observação, atualizar também
        if observacao:
            # Concatenar com observações existentes, se houver
            if insumo.observacoes:
                data["observacoes"] = f"{insumo.observacoes}\n{observacao}"
            else:
                data["observacoes"] = observacao
        
        # Atualizar no repositório
        insumo_atualizado = self.insumo_repository.update(insumo_id, data)
        
        if not insumo_atualizado:
            return False, None, "Erro ao atualizar estoque"
        
        # Verificar se o estoque está abaixo do mínimo após a operação
        if insumo_atualizado.estoque_atual < insumo_atualizado.estoque_minimo:
            return True, insumo_atualizado, f"Estoque atualizado, mas está abaixo do mínimo recomendado ({insumo_atualizado.estoque_minimo})"
        
        return True, insumo_atualizado, f"Estoque atualizado com sucesso. Novo estoque: {insumo_atualizado.estoque_atual}"