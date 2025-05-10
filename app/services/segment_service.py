"""
Serviço para operações CRUD de segmentos
"""

from typing import Optional, Dict, Any, List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.models import Segment
from app.schemas.segment import SegmentCreate, SegmentUpdate, SegmentResponse, PaginatedSegmentResponse


class SegmentService:
    """
    Serviço para operações relacionadas a segmentos
    Implementa as regras de negócio e acesso a dados
    """

    @staticmethod
    def get_segments(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filter_params: Optional[Dict[str, Any]] = None
    ) -> PaginatedSegmentResponse:
        """
        Retorna uma lista paginada de segmentos com opção de filtros
        
        Args:
            db: Sessão do banco de dados
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar (paginação)
            filter_params: Parâmetros para filtragem (opcional)
            
        Returns:
            PaginatedSegmentResponse: Lista paginada de segmentos
        """
        query = db.query(Segment)
        
        # Aplicar filtros se fornecidos
        if filter_params:
            for key, value in filter_params.items():
                if value is not None and hasattr(Segment, key):
                    # Usar LIKE para busca parcial em campos de texto
                    if key == "nome" and isinstance(value, str):
                        query = query.filter(getattr(Segment, key).ilike(f"%{value}%"))
                    elif key == "descricao" and isinstance(value, str):
                        query = query.filter(getattr(Segment, key).ilike(f"%{value}%"))
                    else:
                        # Para outros campos (não texto), usar igualdade exata
                        query = query.filter(getattr(Segment, key) == value)
        
        # Contar total antes de aplicar paginação
        total = query.count()
        
        # Aplicar paginação
        segments = query.offset(skip).limit(limit).all()
        
        # Converter os objetos Segment para dicionários e depois para SegmentResponse
        segment_responses = [SegmentResponse.model_validate(segment) for segment in segments]
        
        # Criar resposta paginada
        return PaginatedSegmentResponse(
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit,
            items=segment_responses
        )
    
    @staticmethod
    def get_segment_by_id(db: Session, segment_id: UUID) -> Optional[Segment]:
        """
        Busca um segmento pelo ID
        
        Args:
            db: Sessão do banco de dados
            segment_id: ID do segmento
            
        Returns:
            Optional[Segment]: Segmento encontrado ou None
        """
        return db.query(Segment).filter(Segment.id == segment_id).first()
    
    @staticmethod
    def get_segment_by_nome(db: Session, nome: str) -> Optional[Segment]:
        """
        Busca um segmento pelo nome
        
        Args:
            db: Sessão do banco de dados
            nome: Nome do segmento
            
        Returns:
            Optional[Segment]: Segmento encontrado ou None
        """
        return db.query(Segment).filter(Segment.nome == nome).first()
    
    @staticmethod
    def create_segment(db: Session, segment_data: SegmentCreate) -> Segment:
        """
        Cria um novo segmento
        
        Args:
            db: Sessão do banco de dados
            segment_data: Dados do novo segmento
            
        Returns:
            Segment: Segmento criado
            
        Raises:
            HTTPException: Se o nome já estiver em uso
        """
        # Verificar se nome já existe
        if SegmentService.get_segment_by_nome(db, segment_data.nome):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome de segmento já está em uso"
            )
        
        # Criar segmento
        db_segment = Segment(
            nome=segment_data.nome,
            descricao=segment_data.descricao,
            is_active=segment_data.is_active
        )
        
        db.add(db_segment)
        db.commit()
        db.refresh(db_segment)
        
        return db_segment
    
    @staticmethod
    def update_segment(db: Session, segment_id: UUID, segment_data: SegmentUpdate) -> Optional[Segment]:
        """
        Atualiza um segmento existente
        
        Args:
            db: Sessão do banco de dados
            segment_id: ID do segmento a ser atualizado
            segment_data: Dados a serem atualizados
            
        Returns:
            Optional[Segment]: Segmento atualizado ou None se não for encontrado
            
        Raises:
            HTTPException: Se o nome já estiver em uso por outro segmento
        """
        # Buscar segmento existente
        db_segment = SegmentService.get_segment_by_id(db, segment_id)
        if not db_segment:
            return None
        
        # Verificar se o novo nome já está em uso por outro segmento
        if segment_data.nome is not None and segment_data.nome != db_segment.nome:
            existing_segment = SegmentService.get_segment_by_nome(db, segment_data.nome)
            if existing_segment and existing_segment.id != segment_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nome de segmento já está em uso por outro segmento"
                )
        
        # Atualizar campos fornecidos
        update_data = segment_data.model_dump(exclude_unset=True)
        
        # Atualizar os campos
        for key, value in update_data.items():
            setattr(db_segment, key, value)
        
        db.commit()
        db.refresh(db_segment)
        
        return db_segment
    
    @staticmethod
    def delete_segment(db: Session, segment_id: UUID) -> bool:
        """
        Exclui um segmento pelo ID
        
        Args:
            db: Sessão do banco de dados
            segment_id: ID do segmento a ser excluído
            
        Returns:
            bool: True se o segmento foi excluído, False se não foi encontrado
        """
        db_segment = SegmentService.get_segment_by_id(db, segment_id)
        if not db_segment:
            return False
        
        db.delete(db_segment)
        db.commit()
        
        return True