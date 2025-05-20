"""
Serviço para gerenciamento de relatórios de custos
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from sqlalchemy import func, desc, and_, or_, extract
from sqlalchemy.orm import Session

from app.db.models_cost_reports import CostReport
from app.db.models_cost_fixed import CostFixed
from app.db.models_cost_variable import CostVariable
from app.db.models_cost_clinical import CostClinical
from app.db.models_insumo import Insumo
from app.schemas.relatorio_custos import (
    RelatorioCustosCreate,
    RelatorioCustosUpdate,
    ReportTypeEnum
)


class RelatorioCustosService:
    """
    Serviço para gerenciamento de relatórios de custos
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def calcular_totais_por_periodo(
        self, 
        subscriber_id: UUID,
        date_from: date,
        date_to: date
    ) -> Dict[str, Decimal]:
        """
        Calcula os totais de custos por categoria para um período específico.
        
        Args:
            subscriber_id: ID do assinante
            date_from: Data inicial do período
            date_to: Data final do período
            
        Returns:
            Dicionário com os totais por categoria de custo
        """
        # Calcular total de custos fixos
        total_fixos = self.db.query(func.sum(CostFixed.valor))\
            .filter(
                CostFixed.subscriber_id == subscriber_id,
                CostFixed.is_active == True,
                CostFixed.data >= date_from,
                CostFixed.data <= date_to
            ).scalar() or Decimal('0.0')
        
        # Calcular total de custos variáveis
        total_variaveis = self.db.query(func.sum(CostVariable.valor))\
            .filter(
                CostVariable.subscriber_id == subscriber_id,
                CostVariable.is_active == True,
                CostVariable.data >= date_from,
                CostVariable.data <= date_to
            ).scalar() or Decimal('0.0')
        
        # Calcular total de custos clínicos
        total_clinicos = self.db.query(func.sum(CostClinical.total_cost))\
            .filter(
                CostClinical.subscriber_id == subscriber_id,
                CostClinical.is_active == True,
                CostClinical.date >= date_from,
                CostClinical.date <= date_to
            ).scalar() or Decimal('0.0')
        
        # Calcular total de custos de insumos (simplificado, baseado no valor_unitario * estoque_atual)
        # Como não temos histórico de estoque, usamos uma estimativa com base nos insumos atuais
        total_insumos = self.db.query(
            func.sum(Insumo.valor_unitario * Insumo.estoque_atual)
        ).filter(
            Insumo.subscriber_id == subscriber_id,
            Insumo.is_active == True
        ).scalar() or Decimal('0.0')
        
        # Fator de ajuste para representar apenas o período selecionado
        # (uma simplificação para demonstração, em um sistema real precisaríamos do histórico)
        fator_ajuste = 0.1  # Assume que 10% do valor total dos insumos foi consumido no período
        total_insumos = total_insumos * Decimal(str(fator_ajuste))
        
        # Calcular o total geral
        total_geral = total_fixos + total_variaveis + total_clinicos + total_insumos
        
        return {
            "total_fixed_costs": total_fixos,
            "total_variable_costs": total_variaveis,
            "total_clinical_costs": total_clinicos,
            "total_supplies_costs": total_insumos,
            "grand_total": total_geral
        }
    
    def obter_datas_para_tipo_relatorio(
        self,
        report_type: ReportTypeEnum,
        reference_date: Optional[date] = None
    ) -> Tuple[date, date, str]:
        """
        Calcula as datas de início e fim do relatório com base no tipo selecionado.
        
        Args:
            report_type: Tipo de relatório (mensal, trimestral, anual, etc.)
            reference_date: Data de referência (padrão: hoje)
            
        Returns:
            Tupla com (data_inicial, data_final, título_sugerido)
        """
        today = reference_date or date.today()
        
        if report_type == ReportTypeEnum.MENSAL:
            # Primeiro dia do mês atual
            start_date = date(today.year, today.month, 1)
            # Último dia do mês
            if today.month == 12:
                end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
            
            title = f"Relatório Mensal - {today.strftime('%B %Y')}"
        
        elif report_type == ReportTypeEnum.TRIMESTRAL:
            # Determinar o trimestre atual
            quarter = (today.month - 1) // 3 + 1
            # Primeiro dia do trimestre
            start_month = 3 * (quarter - 1) + 1
            start_date = date(today.year, start_month, 1)
            # Último dia do trimestre
            if quarter == 4:
                end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(today.year, start_month + 3, 1) - timedelta(days=1)
            
            title = f"Relatório Trimestral - {quarter}º Trimestre {today.year}"
        
        elif report_type == ReportTypeEnum.ANUAL:
            # Ano completo
            start_date = date(today.year, 1, 1)
            end_date = date(today.year, 12, 31)
            
            title = f"Relatório Anual - {today.year}"
        
        else:  # CUSTOMIZADO
            # Para relatórios customizados, retornar datas vazias
            start_date = today
            end_date = today
            title = f"Relatório Customizado - {today.strftime('%d/%m/%Y')}"
        
        return start_date, end_date, title
    
    def criar_relatorio(
        self,
        subscriber_id: UUID,
        data: RelatorioCustosCreate
    ) -> CostReport:
        """
        Cria um novo relatório de custos.
        
        Args:
            subscriber_id: ID do assinante
            data: Dados para criação do relatório
            
        Returns:
            Instância do relatório criado
        """
        # Calcular totais para o período
        totais = self.calcular_totais_por_periodo(
            subscriber_id=subscriber_id,
            date_from=data.date_from,
            date_to=data.date_to
        )
        
        # Criar o relatório
        relatorio = CostReport(
            subscriber_id=subscriber_id,
            date_from=data.date_from,
            date_to=data.date_to,
            report_type=data.report_type,
            title=data.title,
            description=data.description,
            total_fixed_costs=totais["total_fixed_costs"],
            total_variable_costs=totais["total_variable_costs"],
            total_clinical_costs=totais["total_clinical_costs"],
            total_supplies_costs=totais["total_supplies_costs"],
            grand_total=totais["grand_total"]
        )
        
        self.db.add(relatorio)
        self.db.commit()
        self.db.refresh(relatorio)
        
        return relatorio
    
    def obter_relatorio(
        self,
        relatorio_id: UUID,
        subscriber_id: UUID
    ) -> Optional[CostReport]:
        """
        Obtém um relatório pelo ID.
        
        Args:
            relatorio_id: ID do relatório
            subscriber_id: ID do assinante
            
        Returns:
            Instância do relatório ou None se não encontrado
        """
        return self.db.query(CostReport)\
            .filter(
                CostReport.id == relatorio_id,
                CostReport.subscriber_id == subscriber_id,
                CostReport.is_active == True
            ).first()
    
    def listar_relatorios(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        ano: Optional[int] = None
    ) -> Tuple[List[CostReport], int]:
        """
        Lista todos os relatórios de um assinante.
        
        Args:
            subscriber_id: ID do assinante
            skip: Número de registros para pular (paginação)
            limit: Limite de registros
            ano: Filtrar por ano
            
        Returns:
            Tupla com a lista de relatórios e o total
        """
        query = self.db.query(CostReport)\
            .filter(
                CostReport.subscriber_id == subscriber_id,
                CostReport.is_active == True
            )
        
        # Aplicar filtro por ano
        if ano:
            query = query.filter(extract('year', CostReport.date_from) == ano)
        
        # Ordenar por data de criação decrescente
        query = query.order_by(desc(CostReport.created_at))
        
        # Contar registros
        total = query.count()
        
        # Aplicar paginação
        relatorios = query.offset(skip).limit(limit).all()
        
        return relatorios, total
    
    def atualizar_relatorio(
        self,
        relatorio_id: UUID,
        subscriber_id: UUID,
        data: RelatorioCustosUpdate
    ) -> Optional[CostReport]:
        """
        Atualiza um relatório existente.
        
        Args:
            relatorio_id: ID do relatório
            subscriber_id: ID do assinante
            data: Dados para atualização
            
        Returns:
            Instância do relatório atualizado ou None se não encontrado
        """
        relatorio = self.obter_relatorio(relatorio_id, subscriber_id)
        if not relatorio:
            return None
        
        # Flag para indicar se é necessário recalcular os totais
        recalcular = False
        
        # Atualizar campos
        data_dict = data.dict(exclude_unset=True)
        for field, value in data_dict.items():
            if field in ['date_from', 'date_to'] and value:
                recalcular = True
            setattr(relatorio, field, value)
        
        # Recalcular totais se necessário
        if recalcular:
            totais = self.calcular_totais_por_periodo(
                subscriber_id=subscriber_id,
                date_from=relatorio.date_from,
                date_to=relatorio.date_to
            )
            
            relatorio.total_fixed_costs = totais["total_fixed_costs"]
            relatorio.total_variable_costs = totais["total_variable_costs"]
            relatorio.total_clinical_costs = totais["total_clinical_costs"]
            relatorio.total_supplies_costs = totais["total_supplies_costs"]
            relatorio.grand_total = totais["grand_total"]
        
        self.db.commit()
        self.db.refresh(relatorio)
        
        return relatorio
    
    def remover_relatorio(
        self,
        relatorio_id: UUID,
        subscriber_id: UUID
    ) -> bool:
        """
        Remove logicamente um relatório.
        
        Args:
            relatorio_id: ID do relatório
            subscriber_id: ID do assinante
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        relatorio = self.obter_relatorio(relatorio_id, subscriber_id)
        if not relatorio:
            return False
        
        relatorio.is_active = False
        self.db.commit()
        
        return True
    
    def obter_detalhes_custos_por_categoria(
        self,
        subscriber_id: UUID,
        date_from: date,
        date_to: date
    ) -> Dict[str, Any]:
        """
        Obtém detalhes de custos por categoria para um período específico.
        
        Args:
            subscriber_id: ID do assinante
            date_from: Data inicial do período
            date_to: Data final do período
            
        Returns:
            Dicionário com detalhes de custos por categoria
        """
        # 1. Detalhes de custos fixos
        fixos = self.db.query(CostFixed)\
            .filter(
                CostFixed.subscriber_id == subscriber_id,
                CostFixed.is_active == True,
                CostFixed.data >= date_from,
                CostFixed.data <= date_to
            ).order_by(CostFixed.data).all()
        
        # 2. Detalhes de custos variáveis
        variaveis = self.db.query(CostVariable)\
            .filter(
                CostVariable.subscriber_id == subscriber_id,
                CostVariable.is_active == True,
                CostVariable.data >= date_from,
                CostVariable.data <= date_to
            ).order_by(CostVariable.data).all()
        
        # 3. Detalhes de custos clínicos
        clinicos = self.db.query(CostClinical)\
            .filter(
                CostClinical.subscriber_id == subscriber_id,
                CostClinical.is_active == True,
                CostClinical.date >= date_from,
                CostClinical.date <= date_to
            ).order_by(CostClinical.date).all()
        
        # 4. Detalhes de custos de insumos
        insumos_movimentos = self.db.query(
            HistoricoEstoque.insumo_id,
            Insumo.nome,
            func.sum(HistoricoEstoque.quantidade_movimentada).label('quantidade'),
            func.sum(HistoricoEstoque.quantidade_movimentada * HistoricoEstoque.valor_unitario).label('total')
        ).join(Insumo, HistoricoEstoque.insumo_id == Insumo.id)\
            .filter(
                Insumo.subscriber_id == subscriber_id,
                HistoricoEstoque.tipo_movimento == 'saida',
                HistoricoEstoque.data_movimento >= date_from,
                HistoricoEstoque.data_movimento <= date_to
            ).group_by(
                HistoricoEstoque.insumo_id,
                Insumo.nome
            ).all()
        
        # Formatar detalhes para retornar
        return {
            "custos_fixos": [
                {
                    "id": str(custo.id),
                    "nome": custo.nome,
                    "valor": float(custo.valor),
                    "data": custo.data.isoformat(),
                    "observacoes": custo.observacoes
                } for custo in fixos
            ],
            "custos_variaveis": [
                {
                    "id": str(custo.id),
                    "nome": custo.nome,
                    "categoria": custo.categoria,
                    "valor": float(custo.valor),
                    "data": custo.data.isoformat(),
                    "observacoes": custo.observacoes
                } for custo in variaveis
            ],
            "custos_clinicos": [
                {
                    "id": str(custo.id),
                    "procedure_name": custo.procedure_name,
                    "duration_hours": float(custo.duration_hours),
                    "hourly_rate": float(custo.hourly_rate),
                    "total_cost": float(custo.total_cost),
                    "date": custo.date.isoformat(),
                    "observacoes": custo.observacoes
                } for custo in clinicos
            ],
            "custos_insumos": [
                {
                    "insumo_id": str(movimento[0]),
                    "nome": movimento[1],
                    "quantidade": float(movimento[2]),
                    "total": float(movimento[3])
                } for movimento in insumos_movimentos
            ]
        }
    
    def calcular_distribuicao_percentual(
        self,
        subscriber_id: UUID,
        date_from: date,
        date_to: date
    ) -> Dict[str, float]:
        """
        Calcula a distribuição percentual de custos por categoria.
        
        Args:
            subscriber_id: ID do assinante
            date_from: Data inicial do período
            date_to: Data final do período
            
        Returns:
            Dicionário com percentuais por categoria
        """
        totais = self.calcular_totais_por_periodo(
            subscriber_id=subscriber_id,
            date_from=date_from,
            date_to=date_to
        )
        
        total_geral = float(totais["grand_total"])
        if total_geral == 0:
            return {
                "fixos": 0,
                "variaveis": 0,
                "clinicos": 0,
                "insumos": 0
            }
        
        return {
            "fixos": round(float(totais["total_fixed_costs"]) / total_geral * 100, 2),
            "variaveis": round(float(totais["total_variable_costs"]) / total_geral * 100, 2),
            "clinicos": round(float(totais["total_clinical_costs"]) / total_geral * 100, 2),
            "insumos": round(float(totais["total_supplies_costs"]) / total_geral * 100, 2)
        }
    
    def calcular_evolucao_mensal(
        self,
        subscriber_id: UUID,
        date_from: date,
        date_to: date
    ) -> List[Dict[str, Any]]:
        """
        Calcula a evolução mensal de custos no período.
        
        Args:
            subscriber_id: ID do assinante
            date_from: Data inicial do período
            date_to: Data final do período
            
        Returns:
            Lista com valores mensais por categoria
        """
        # Determinar quantos meses há no período
        meses = []
        current_date = date(date_from.year, date_from.month, 1)
        end_month = date(date_to.year, date_to.month, 1)
        
        while current_date <= end_month:
            # Início do mês atual
            start_of_month = current_date
            
            # Fim do mês atual
            if current_date.month == 12:
                end_of_month = date(current_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_of_month = date(current_date.year, current_date.month + 1, 1) - timedelta(days=1)
            
            # Calcular totais para este mês
            totais = self.calcular_totais_por_periodo(
                subscriber_id=subscriber_id,
                date_from=start_of_month,
                date_to=end_of_month
            )
            
            # Adicionar à lista de meses
            meses.append({
                "mes": start_of_month.strftime("%Y-%m"),
                "nome_mes": start_of_month.strftime("%B/%Y"),
                "fixos": float(totais["total_fixed_costs"]),
                "variaveis": float(totais["total_variable_costs"]),
                "clinicos": float(totais["total_clinical_costs"]),
                "insumos": float(totais["total_supplies_costs"]),
                "total": float(totais["grand_total"])
            })
            
            # Avançar para o próximo mês
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)
        
        return meses