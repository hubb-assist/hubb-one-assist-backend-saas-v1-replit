"""
Entidades de domínio para o módulo de Insumos.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from app.domain.insumo.value_objects.modulo_association import ModuloAssociation


class InsumoEntity:
    """
    Entidade de domínio para representar um Insumo (Suprimento).
    
    Esta entidade contém toda a lógica de negócio relacionada a insumos,
    garantindo a consistência dos dados e as regras do domínio.
    """
    
    def __init__(
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
        data_validade: Optional[datetime] = None,
        data_compra: Optional[datetime] = None,
        observacoes: Optional[str] = None,
        id: Optional[UUID] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        modules_used: Optional[List[ModuloAssociation]] = None
    ):
        """
        Inicializa uma nova entidade de Insumo.
        
        Args:
            nome: Nome do insumo
            descricao: Descrição detalhada do insumo
            categoria: Categoria do insumo (ex: "medicamento", "material")
            valor_unitario: Valor unitário do insumo
            unidade_medida: Unidade de medida (ex: "unidade", "ml", "caixa")
            estoque_minimo: Estoque mínimo recomendado
            estoque_atual: Quantidade atual em estoque
            subscriber_id: ID do assinante (isolamento multitenant)
            fornecedor: Nome do fornecedor (opcional)
            codigo_referencia: Código de referência (opcional)
            data_validade: Data de validade (opcional)
            data_compra: Data da última compra (opcional)
            observacoes: Observações adicionais (opcional)
            id: UUID do insumo, gerado automaticamente se não fornecido
            is_active: Indica se o insumo está ativo
            created_at: Data de criação
            updated_at: Data da última atualização
            modules_used: Lista de associações com módulos
        """
        # Validação de campos
        self._validar_campos_obrigatorios(
            nome, descricao, categoria, valor_unitario, 
            unidade_medida, estoque_minimo, estoque_atual, subscriber_id
        )
        
        # Atribuição de campos
        self.id = id if id else uuid4()
        self.nome = nome
        self.descricao = descricao
        self.categoria = categoria
        self.valor_unitario = valor_unitario
        self.unidade_medida = unidade_medida
        self.estoque_minimo = estoque_minimo
        self.estoque_atual = estoque_atual
        self.subscriber_id = subscriber_id
        self.fornecedor = fornecedor
        self.codigo_referencia = codigo_referencia
        self.data_validade = data_validade
        self.data_compra = data_compra
        self.observacoes = observacoes
        self.is_active = is_active
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()
        self.modules_used = modules_used if modules_used else []

    def _validar_campos_obrigatorios(
        self, nome, descricao, categoria, valor_unitario, 
        unidade_medida, estoque_minimo, estoque_atual, subscriber_id
    ):
        """
        Valida os campos obrigatórios da entidade.
        
        Raises:
            ValueError: Se algum campo obrigatório for inválido
        """
        # Validar campos em branco ou nulos
        if not nome or not descricao or not categoria or not unidade_medida:
            raise ValueError("Campos obrigatórios não podem ser vazios")
            
        # Validar campos numéricos
        if valor_unitario < 0:
            raise ValueError("Valor unitário não pode ser negativo")
            
        if estoque_minimo < 0:
            raise ValueError("Estoque mínimo não pode ser negativo")
            
        if estoque_atual < 0:
            raise ValueError("Estoque atual não pode ser negativo")
            
        # Validar subscriber_id
        if not subscriber_id:
            raise ValueError("Subscriber ID é obrigatório")
            
    def esta_abaixo_do_minimo(self) -> bool:
        """
        Verifica se o estoque atual está abaixo do mínimo.
        
        Returns:
            bool: True se estiver abaixo do mínimo, False caso contrário
        """
        return self.estoque_atual < self.estoque_minimo
        
    def adicionar_estoque(self, quantidade: int) -> int:
        """
        Adiciona quantidade ao estoque atual.
        
        Args:
            quantidade: Quantidade a adicionar (deve ser positiva)
            
        Returns:
            int: Novo valor do estoque
            
        Raises:
            ValueError: Se a quantidade for negativa
        """
        if quantidade <= 0:
            raise ValueError("Quantidade a adicionar deve ser positiva")
            
        self.estoque_atual += quantidade
        self.updated_at = datetime.utcnow()
        return self.estoque_atual
        
    def reduzir_estoque(self, quantidade: int) -> int:
        """
        Reduz quantidade do estoque atual.
        
        Args:
            quantidade: Quantidade a reduzir (deve ser positiva)
            
        Returns:
            int: Novo valor do estoque
            
        Raises:
            ValueError: Se a quantidade for negativa ou maior que o estoque atual
        """
        if quantidade <= 0:
            raise ValueError("Quantidade a reduzir deve ser positiva")
            
        if quantidade > self.estoque_atual:
            raise ValueError("Quantidade a reduzir não pode ser maior que o estoque atual")
            
        self.estoque_atual -= quantidade
        self.updated_at = datetime.utcnow()
        return self.estoque_atual
        
    def esta_expirado(self) -> bool:
        """
        Verifica se o insumo está expirado, baseado na data de validade.
        
        Returns:
            bool: True se expirado, False caso contrário ou se não tiver data de validade
        """
        if not self.data_validade:
            return False
            
        return self.data_validade < datetime.utcnow()
        
    def atualizar_dados(self, dados_atualizados: dict) -> None:
        """
        Atualiza os dados da entidade com base em um dicionário.
        
        Args:
            dados_atualizados: Dicionário com os campos a atualizar
            
        Raises:
            ValueError: Se os dados atualizados forem inválidos
        """
        # Campos que não podem ser atualizados diretamente
        campos_protegidos = ["id", "subscriber_id", "created_at"]
        
        # Validar campos protegidos
        for campo in campos_protegidos:
            if campo in dados_atualizados:
                dados_atualizados.pop(campo)
                
        # Validar campos numéricos
        if "valor_unitario" in dados_atualizados and dados_atualizados["valor_unitario"] < 0:
            raise ValueError("Valor unitário não pode ser negativo")
            
        if "estoque_minimo" in dados_atualizados and dados_atualizados["estoque_minimo"] < 0:
            raise ValueError("Estoque mínimo não pode ser negativo")
            
        # Atualizar campos
        for chave, valor in dados_atualizados.items():
            if hasattr(self, chave):
                setattr(self, chave, valor)
                
        # Atualizar timestamp de modificação
        self.updated_at = datetime.utcnow()
        
    def desativar(self) -> None:
        """
        Desativa o insumo (exclusão lógica).
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()
        
    def reativar(self) -> None:
        """
        Reativa o insumo.
        """
        self.is_active = True
        self.updated_at = datetime.utcnow()