# HUBB ONE Assist SaaS API

Esta é uma API backend para o HUBB ONE Assist SaaS construída usando FastAPI. A API inclui autenticação JWT, integração com PostgreSQL, e segue os princípios de arquitetura limpa.

## Estrutura do Projeto

```
├── app                 # Diretório principal da aplicação
│   ├── api             # Rotas da API
│   ├── core            # Configurações e funcionalidades centrais
│   ├── db              # Modelos de banco de dados e repositórios
│   ├── schemas         # Esquemas Pydantic para validação de dados
│   ├── services        # Lógica de negócios
│   └── utils           # Utilitários
├── alembic             # Migrações de banco de dados
└── scripts             # Scripts auxiliares
```

## Como Executar

Este projeto precisa ser executado em duas partes para funcionar corretamente:

### 1. Servidor de Frontend (Gunicorn)

Este servidor é iniciado automaticamente pelo Replit e serve a página inicial com instruções.

```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

### 2. Servidor de API (Uvicorn)

**IMPORTANTE**: Para acessar a documentação Swagger e usar a API, é necessário iniciar o servidor Uvicorn separadamente.

Em um novo terminal, execute:

```bash
./run-uvicorn.sh
```

ou

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'
```

## Acessando a API

- **API Root**: `/`
- **Documentação Swagger UI**: `/api/v1/docs`
- **Documentação ReDoc**: `/api/v1/redoc`

## Endpoints Disponíveis

- **Autenticação**:
  - `/api/v1/auth/login`: Autenticação de usuários
  - `/api/v1/auth/refresh`: Renovação de token JWT

- **Usuários**:
  - `/api/v1/users`: CRUD de usuários

## Tecnologias Utilizadas

- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT para autenticação
- Uvicorn/Gunicorn como servidores ASGI/WSGI

## Desenvolvimento

Para desenvolvimento local, é recomendado iniciar o servidor Uvicorn com a flag `--reload` para atualização automática ao editar os arquivos:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```