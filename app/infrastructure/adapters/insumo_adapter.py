"""
Adaptador para converter entre entidades de domínio e modelos ORM para insumos.
"""
from typing import Optional, List
from decimal import Decimal
from app.domain.insumo.entities import InsumoEntity
from app.db.models.insumo import Insumo, Modulo


class InsumoAdapter:
    """
    Classe adaptadora que converte entre InsumoEntity (domínio) e Insumo (ORM).
    Lida com a conversão entre modelos de dados simples (ORM) e entidades ricas.
    """
    
    @staticmethod
    def to_entity(orm_model: Insumo) -> Optional[InsumoEntity]:
        """
        Converte um modelo ORM de insumo em uma entidade de domínio.
        
        Args:
            orm_model: Modelo ORM de Insumo
            
        Returns:
            Optional[InsumoEntity]: Entidade de domínio equivalente ou None
        """
        if not orm_model:
            return None
            
        # Extrair valores dos atributos do modelo ORM
        modulos = [modulo.name for modulo in orm_model.modulos]
        valor = Decimal(str(orm_model.valor))
            
        return InsumoEntity(
            id=orm_model.id,
            subscriber_id=orm_model.subscriber_id,
            nome=orm_model.nome,
            tipo=orm_model.tipo,
            unidade=orm_model.unidade,
            valor=valor,
            observacoes=orm_model.observacoes,
            categoria=orm_model.categoria,
            modulos=modulos,
            is_active=orm_model.is_active,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at
        )
    
    @staticmethod
    def to_orm_model(entity: InsumoEntity, db_session, orm_model: Insumo = None) -> Insumo:
        """
        Converte uma entidade de domínio para um modelo ORM.
        Se um modelo ORM for fornecido, apenas atualiza seus atributos.
        
        Args:
            entity: Entidade de domínio de insumo
            db_session: Sessão de banco de dados para consultar/criar módulos
            orm_model: Modelo ORM opcional para atualizar (em vez de criar)
            
        Returns:
            Insumo: Modelo ORM atualizado ou criado
        """
        if not entity:
            return None
            
        # Recuperar ou criar objetos de Modulo
        modulos = []
        for modulo_name in entity.modulos:
            modulo = db_session.query(Modulo).filter_by(name=modulo_name).first()
            if not modulo:
                modulo = Modulo(name=modulo_name)
                db_session.add(modulo)
            modulos.append(modulo)
        
        # Dados para o modelo ORM
        insumo_data = {
            'nome': entity.nome,
            'tipo': entity.tipo,
            'unidade': entity.unidade,
            'valor': entity.valor,
            'observacoes': entity.observacoes,
            'categoria': entity.categoria,
            'is_active': entity.is_active,
            'subscriber_id': entity.subscriber_id,
        }
            
        if not orm_model:
            # Criar novo modelo ORM
            insumo_data['id'] = entity.id
            insumo_data['created_at'] = entity.created_at
            insumo_data['updated_at'] = entity.updated_at
            
            orm_model = Insumo(**insumo_data)
            orm_model.modulos = modulos
        else:
            # Atualizar modelo existente
            for key, value in insumo_data.items():
                setattr(orm_model, key, value)
            orm_model.updated_at = entity.updated_at
            orm_model.modulos = modulos
        
        return orm_model
    
    @staticmethod
    def extract_simple_data(entity: InsumoEntity) -> dict:
        """
        Extrai dados simples de uma entidade rica.
        Útil para serialização e APIs.
        
        Args:
            entity: Entidade de domínio de insumo
            
        Returns:
            dict: Dados em formato simples adequado para JSON
        """
        return {
            'id': str(entity.id),
            'subscriber_id': str(entity.subscriber_id),
            'nome': entity.nome,
            'tipo': entity.tipo,
            'unidade': entity.unidade,
            'valor': str(entity.valor),
            'observacoes': entity.observacoes,
            'categoria': entity.categoria,
            'modulos': entity.modulos,
            'is_active': entity.is_active,
            'created_at': entity.created_at.isoformat() if entity.created_at else None,
            'updated_at': entity.updated_at.isoformat() if entity.updated_at else None
        }