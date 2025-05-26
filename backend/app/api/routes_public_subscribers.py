"""
Rotas públicas da API para criação de assinantes sem autenticação
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

from app.db.session import get_db
from app.schemas.subscriber import SubscriberCreate
from app.services.subscriber_service import SubscriberService

# Definir o router
router = APIRouter(
    prefix="/public/subscribers",
    tags=["public"],
    responses={
        400: {"description": "Requisição inválida"},
        409: {"description": "Conflito - Email ou documento já cadastrado"},
        404: {"description": "Recurso não encontrado"},
        500: {"description": "Erro interno do servidor"}
    },
)


# Schema específico para a API pública, usando a mesma estrutura do SubscriberCreate
class PublicSubscriberCreate(BaseModel):
    """Schema para criação pública de assinante durante onboarding"""
    name: str = Field(..., min_length=2, max_length=100, description="Nome do responsável")
    clinic_name: str = Field(..., min_length=2, max_length=100, description="Nome da clínica")
    email: EmailStr = Field(..., description="Email de contato principal")
    phone: str = Field(..., description="Telefone de contato")
    document: str = Field(..., description="CPF ou CNPJ")
    zip_code: str = Field(..., description="CEP")
    address: str = Field(..., description="Logradouro/rua")
    number: str = Field(..., description="Número do endereço")
    city: str = Field(..., description="Cidade")
    state: str = Field(..., max_length=2, description="Estado (UF)")
    segment_id: UUID = Field(..., description="ID do segmento ao qual o assinante pertence")
    plan_id: UUID = Field(..., description="ID do plano contratado")
    password: str = Field(..., min_length=8, description="Senha do usuário administrador")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_public_subscriber(
    subscriber_data: PublicSubscriberCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um novo assinante a partir do processo de onboarding público.
    Este endpoint é acessível sem autenticação, mas protegido por CORS.
    
    Cria um assinante e automaticamente cria um usuário administrador com a role DONO_ASSINANTE.
    
    Args:
        subscriber_data: Dados do novo assinante
        db: Sessão do banco de dados
        
    Returns:
        dict: Mensagem de sucesso e ID do assinante criado
        
    Raises:
        HTTPException: Se houver erros de validação ou conflitos
    """
    try:
        # Converter para o schema interno
        internal_subscriber_data = SubscriberCreate(
            name=subscriber_data.name,
            clinic_name=subscriber_data.clinic_name,
            email=subscriber_data.email,
            phone=subscriber_data.phone,
            document=subscriber_data.document,
            zip_code=subscriber_data.zip_code,
            address=subscriber_data.address,
            number=subscriber_data.number,
            city=subscriber_data.city,
            state=subscriber_data.state,
            segment_id=subscriber_data.segment_id,
            plan_id=subscriber_data.plan_id,
            admin_password=subscriber_data.password,
            is_active=True
        )
        
        # Utilizar o serviço existente para criar o assinante e seu usuário admin
        new_subscriber = SubscriberService.create_subscriber(db, internal_subscriber_data)
        
        # Retornar resposta de sucesso
        return {
            "message": "Assinante criado com sucesso",
            "id": str(new_subscriber.id)
        }
        
    except HTTPException as he:
        # Repassar exceções HTTP geradas pelo serviço
        raise he
    except Exception as e:
        # Log do erro e resposta genérica para outros erros
        print(f"[ERROR] Erro ao criar assinante público: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação. Por favor, tente novamente."
        )