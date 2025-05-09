# API REST Simples com FastAPI

Uma API REST básica construída com FastAPI em Python para demonstrar funcionalidades CRUD, tratamento de erros e documentação automática.

## Funcionalidades

- ✅ API REST construída com FastAPI
- ✅ Operações CRUD básicas
- ✅ Respostas em formato JSON
- ✅ Tratamento adequado de erros
- ✅ Documentação com Swagger UI e ReDoc
- ✅ Implementação de modelo de dados básico
- ✅ Validação de entrada de dados
- ✅ Banco de dados em memória

## Estrutura do Projeto

```
.
├── fastapi_app.py           # Aplicação principal FastAPI
├── run.py                   # Script para executar o servidor
├── start-server.sh          # Shell script para iniciar o servidor
└── README.md                # Este arquivo README
```

## Como Executar

### Opção 1: Usando Python diretamente

```bash
python -m uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

### Opção 2: Usando o script Python

```bash
python run.py
```

### Opção 3: Usando o shell script

```bash
./start-server.sh
```

## Acessando a API

- **Documentação Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Documentação ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Endpoint Raiz**: [http://localhost:8000/](http://localhost:8000/)

## Endpoints Disponíveis

- `GET /` - Informações sobre a API
- `GET /items` - Listar todos os itens (com paginação e filtros)
- `GET /items/{item_id}` - Obter um item específico
- `POST /items` - Criar um novo item
- `PUT /items/{item_id}` - Atualizar um item existente
- `DELETE /items/{item_id}` - Remover um item

## Tecnologias Utilizadas

- Python 3.x
- FastAPI
- Uvicorn (servidor ASGI)
- Pydantic para validação de dados

## Próximos Passos

- [ ] Integração com banco de dados
- [ ] Sistema de autenticação
- [ ] Limitação de taxa de requisições
- [ ] Tratamento de requisições assíncronas