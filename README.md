# HUBB ONE Assist - Monorepo Full Stack

Sistema SaaS completo para gestão financeira profissional de clínicas e consultórios médicos.

## Estrutura do Projeto

```
hubb-one-assist-monorepo/
├── backend/        # API FastAPI com arquitetura DDD
├── frontend/       # App React + Vite + TypeScript  
├── shared/         # Tipos e utilitários compartilhados
└── README.md
```

### Backend
- FastAPI com arquitetura Domain-Driven Design (DDD)
- PostgreSQL com SQLAlchemy ORM
- Autenticação JWT com controle de acesso baseado em roles
- Módulos completos: Financeiro, Pacientes, Agendamentos, Insumos

### Frontend  
- React 18 + Vite + TypeScript
- Tipos gerados automaticamente a partir da API OpenAPI
- Cliente HTTP tipado para comunicação com backend

### Shared
- Tipos TypeScript gerados automaticamente
- Utilitários e constantes compartilhadas

## Deploy

URL de produção: https://hubb-one-assist-front-e-back-monol-hubb-one.replit.app

## Desenvolvimento

Para executar o projeto em desenvolvimento:

```bash
# Backend (porta 8000)
cd backend && uvicorn app.main:app --reload

# Frontend (porta 5173) 
cd frontend && npm run dev
```

## Tecnologias

**Backend:**
- Python 3.11, FastAPI, SQLAlchemy, PostgreSQL, Alembic

**Frontend:**
- React 18, TypeScript, Vite, Axios

**Shared:**
- OpenAPI TypeScript codegen para tipos seguros