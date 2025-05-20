"""
Entidades do domínio de Insumos.
"""

from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID, uuid4

from app.domain.insumo.value_objects.modulo_association import ModuloAssociation


class InsumoEntity:
    """
    Entidade que representa um insumo no domínio de negócio.
    
    Esta classe contém todas as regras de negócio relacionadas
    a insumos, materiais e produtos utilizados na operação.
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
        id: Optional[UUID] = None,
        fornecedor: Optional[str] = None,
        codigo_referencia: Optional[str] = None,
        data_validade: Optional[datetime] = None,
        data_compra: Optional[datetime] = None,
        observacoes: Optional[str] = None,
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
            categoria: Categoria do insumo (ex: material, medicamento, etc)
            valor_unitario: Valor unitário do insumo
            unidade_medida: Unidade de medida do insumo (ex: un, kg, ml, etc)
            estoque_minimo: Quantidade mínima que deve ser mantida em estoque
            estoque_atual: Quantidade atual em estoque
            subscriber_id: ID do assinante proprietário do insumo
            id: Identificador único, gerado automaticamente se não fornecido
            fornecedor: Nome do fornecedor ou fabricante
            codigo_referencia: Código de referência do fornecedor
            data_validade: Data de validade do insumo
            data_compra: Data da última compra
            observacoes: Observações adicionais
            is_active: Indica se o insumo está ativo
            created_at: Data de criação
            updated_at: Data da última atualização
            modules_used: Lista de associações com módulos funcionais
        """
        # Validações básicas
        if valor_unitario < 0:
            raise ValueError("Valor unitário não pode ser negativo")
            
        if estoque_minimo < 0:
            raise ValueError("Estoque mínimo não pode ser negativo")
            
        if estoque_atual < 0:
            raise ValueError("Estoque atual não pode ser negativo")
        
        # Propriedades obrigatórias
        self.id = id or uuid4()
        self.nome = nome
        self.descricao = descricao
        self.categoria = categoria
        self.valor_unitario = valor_unitario
        self.unidade_medida = unidade_medida
        self.estoque_minimo = estoque_minimo
        self.estoque_atual = estoque_atual
        self.subscriber_id = subscriber_id
        
        # Propriedades opcionais
        self.fornecedor = fornecedor
        self.codigo_referencia = codigo_referencia
        self.observacoes = observacoes
        self.is_active = is_active
        
        # Datas
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        
        # Data de validade
        self.data_validade = None
        if data_validade:
            if data_validade < datetime.utcnow():
                # Não lançar erro, apenas marcar que o produto está vencido
                self.data_validade = data_validade
            else:
                self.data_validade = data_validade
        
        # Data de compra
        self.data_compra = None
        if data_compra:
            if data_compra > datetime.utcnow():
                raise ValueError("Data de compra não pode ser futura")
            self.data_compra = data_compra
                
        # Associações com módulos
        self.modules_used = modules_used or []
    
    def verificar_estoque_baixo(self) -> bool:
        """
        Verifica se o estoque está abaixo do mínimo definido.
        
        Returns:
            bool: True se o estoque está abaixo do mínimo, False caso contrário
        """
        return self.estoque_atual < self.estoque_minimo
    
    def verificar_validade(self) -> bool:
        """
        Verifica se o insumo está dentro do prazo de validade.
        
        Returns:
            bool: True se o insumo está válido, False se está vencido ou não tem data de validade
        """
        if not self.data_validade:
            return False  # Se não tem data, consideramos como não validado
            
        return self.data_validade > datetime.utcnow()
    
    def calcular_valor_total(self) -> float:
        """
        Calcula o valor total do insumo em estoque.
        
        Returns:
            float: Valor total do estoque (quantidade atual * valor unitário)
        """
        return self.estoque_atual * self.valor_unitario
    
    def atualizar_estoque(self, quantidade: int, tipo_movimento: str) -> None:
        """
        Atualiza o estoque atual com base em um movimento de entrada ou saída.
        
        Args:
            quantidade: Quantidade a ser movimentada (sempre positiva)
            tipo_movimento: Tipo de movimento ('entrada' ou 'saida')
            
        Raises:
            ValueError: Se a quantidade for negativa ou tipo de movimento inválido
            ValueError: Se a retirada resultar em estoque negativo
        """
        if quantidade < 0:
            raise ValueError("A quantidade deve ser um valor positivo")
            
        if tipo_movimento not in ['entrada', 'saida']:
            raise ValueError("Tipo de movimento deve ser 'entrada' ou 'saida'")
            
        if tipo_movimento == 'entrada':
            self.estoque_atual += quantidade
        else:  # saída
            if self.estoque_atual < quantidade:
                raise ValueError(f"Estoque insuficiente. Disponível: {self.estoque_atual}, Solicitado: {quantidade}")
            self.estoque_atual -= quantidade
            
        # Atualizar data de modificação
        self.updated_at = datetime.utcnow()
        
    def atualizar_campos(self, dados: dict) -> None:
        """
        Atualiza os campos da entidade com base em um dicionário de dados.
        
        Args:
            dados: Dicionário com os campos a serem atualizados
            
        Raises:
            ValueError: Se algum valor de campo for inválido
        """
        # Atualizar campos de texto
        if 'nome' in dados and dados['nome'] is not None:
            self.nome = dados['nome']
            
        if 'descricao' in dados and dados['descricao'] is not None:
            self.descricao = dados['descricao']
            
        if 'categoria' in dados and dados['categoria'] is not None:
            self.categoria = dados['categoria']
            
        if 'unidade_medida' in dados and dados['unidade_medida'] is not None:
            self.unidade_medida = dados['unidade_medida']
            
        if 'fornecedor' in dados:
            self.fornecedor = dados['fornecedor']
            
        if 'codigo_referencia' in dados:
            self.codigo_referencia = dados['codigo_referencia']
            
        if 'observacoes' in dados:
            self.observacoes = dados['observacoes']
        
        # Atualizar campos numéricos com validação
        if 'valor_unitario' in dados and dados['valor_unitario'] is not None:
            if dados['valor_unitario'] < 0:
                raise ValueError("Valor unitário não pode ser negativo")
            self.valor_unitario = dados['valor_unitario']
            
        if 'estoque_minimo' in dados and dados['estoque_minimo'] is not None:
            if dados['estoque_minimo'] < 0:
                raise ValueError("Estoque mínimo não pode ser negativo")
            self.estoque_minimo = dados['estoque_minimo']
            
        if 'estoque_atual' in dados and dados['estoque_atual'] is not None:
            if dados['estoque_atual'] < 0:
                raise ValueError("Estoque atual não pode ser negativo")
            self.estoque_atual = dados['estoque_atual']
            
        # Atualizar datas com validação
        if 'data_validade' in dados:
            self.data_validade = dados['data_validade']
            
        if 'data_compra' in dados:
            if dados['data_compra'] and dados['data_compra'] > datetime.utcnow():
                raise ValueError("Data de compra não pode ser futura")
            self.data_compra = dados['data_compra']
            
        # Atualizar associações com módulos
        if 'modules_used' in dados and dados['modules_used'] is not None:
            self.modules_used = dados['modules_used']
            
        # Atualizar data de modificação
        self.updated_at = datetime.utcnow()