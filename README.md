# API REST Simples - FastAPI

API REST simples construída com FastAPI, focando na implementação de operações CRUD básicas para um modelo simples de itens.

## Sobre o Projeto

Este projeto é uma API REST desenvolvida com FastAPI, que fornece operações CRUD simples com armazenamento em memória. A API inclui documentação interativa automática usando Swagger UI.

## Funcionalidades

- Operações CRUD completas para o modelo `Item`
- Paginação e filtragem de dados
- Validação de dados usando Pydantic
- Documentação interativa com Swagger UI
- Resposta HTML na rota raiz com informações sobre a API

## Estrutura do Projeto

```
.
├── app/
│   ├── __init__.py
│   └── main.py         # Aplicação FastAPI principal
├── main.py             # Importa e exporta a aplicação
├── wsgi.py             # Adaptador ASGI para WSGI
└── start-fastapi.sh    # Script para iniciar o servidor
```

## Endpoints

A API oferece os seguintes endpoints:

- `GET /`: Página inicial com informações sobre a API
- `GET /api-info`: Informações básicas sobre a API
- `GET /items`: Listar todos os itens com opções de paginação e filtro
- `GET /items/{item_id}`: Obter um item específico por ID
- `POST /items`: Criar um novo item
- `PUT /items/{item_id}`: Atualizar um item existente
- `DELETE /items/{item_id}`: Remover um item

## Documentação

A documentação interativa está disponível em:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Como Executar

Para iniciar o servidor usando uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

Ou use o script shell fornecido:

```bash
./start-fastapi.sh
```

## Tecnologias Utilizadas

- Python 3.11
- FastAPI
- Pydantic para validação de dados
- Uvicorn como servidor ASGI
- Gunicorn como servidor WSGI com adaptador ASGI