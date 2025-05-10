# API REST Simples - FastAPI

API REST simples construída com FastAPI, focando na implementação de operações CRUD básicas para um modelo simples de itens.

## Sobre o Projeto

Este projeto é uma API REST desenvolvida com FastAPI, que fornece operações CRUD simples com armazenamento em memória. A API inclui documentação interativa automática usando Swagger UI e adota os princípios SOLID, DDD (Domain-Driven Design) e Clean Code.

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

## Princípios de Desenvolvimento Adotados

### Princípios SOLID

1. **S — Single Responsibility Principle (Princípio da Responsabilidade Única)**
   - Cada módulo ou classe deve ter uma única responsabilidade, e essa responsabilidade deve estar completamente encapsulada.
   - Aplicação no projeto:
     - Cada camada tem responsabilidade clara:
       - `app/api/`: somente define rotas e recebe requisições.
       - `app/services/`: concentra as regras de negócio (casos de uso).
       - `app/db/models/`: define a estrutura do banco.
       - `app/schemas/`: define as validações de entrada e saída.
       - `app/core/`: configurações gerais, autenticação, segurança.

2. **O — Open/Closed Principle (Aberto para Extensão, Fechado para Modificação)**
   - Entidades devem estar abertas para extensão, mas fechadas para modificação.
   - Aplicação no projeto:
     - O backend será modular: novos módulos podem ser adicionados sem alterar os existentes.
     - Utilização de interfaces e serviços desacoplados.

3. **L — Liskov Substitution Principle (Princípio da Substituição de Liskov)**
   - Objetos devem poder ser substituídos por instâncias de suas subclasses sem afetar o funcionamento do sistema.
   - Aplicação no projeto:
     - Serviços e controladores usarão tipagem explícita e Pydantic com herança segura.
     - Em testes, será possível substituir classes de serviços reais por mocks.

4. **I — Interface Segregation Principle (Princípio da Segregação de Interface)**
   - Muitos contratos específicos são melhores do que um contrato único e geral.
   - Aplicação no projeto:
     - Os endpoints e serviços seguirão contratos pequenos e separados.
     - Separação clara de rotas por domínio.

5. **D — Dependency Inversion Principle (Princípio da Inversão de Dependência)**
   - Módulos de alto nível não devem depender de módulos de baixo nível, ambos devem depender de abstrações.
   - Aplicação no projeto:
     - Utilização de injeção de dependência do FastAPI.
     - Serviços de repositório e lógica de negócio serão injetados, nunca instanciados diretamente.

### Domain-Driven Design (DDD)

O projeto é estruturado seguindo princípios de DDD para manter a complexidade do sistema sob controle ao modelar o código diretamente com base na lógica de negócio real.

#### Camadas do Projeto com DDD

1. **Camada de Domínio** (`app/services/` e `app/schemas/`)
   - Representa a lógica de negócio central.
   - Cada serviço de domínio encapsula um "caso de uso".
   - Essa camada não depende de FastAPI, banco ou rotas.

2. **Camada de Aplicação** (`app/api/`)
   - Responsável por expor a aplicação ao mundo exterior (HTTP).
   - Define as rotas e orquestra chamadas aos serviços de domínio.
   - Essa camada não implementa regra de negócio, apenas chama os casos de uso.

3. **Camada de Infraestrutura** (`app/db/` e `app/core/`)
   - Contém os detalhes técnicos: acesso ao banco, migrações, autenticação, middlewares, etc.
   - Também pode conter serviços de integração externa.
   - Essas implementações são injetadas como dependências.

### Clean Code

O código segue princípios de Clean Code para garantir legibilidade, manutenibilidade e qualidade:

1. **Nomeação clara e sem ambiguidade**
   - Funções, variáveis, rotas e arquivos têm nomes descritivos com intenção explícita.
   - Pastas organizadas por contexto, não por tipo genérico.

2. **Funções pequenas com responsabilidade única**
   - Nenhuma função faz mais de uma coisa.
   - Regras complexas são quebradas em pequenos métodos reutilizáveis.

3. **Sem código duplicado**
   - Qualquer lógica repetida é extraída para funções utilitárias.

4. **Tratamento explícito de erros**
   - Exceções são tratadas com mensagens claras, usando o sistema de HTTPException.
   - Logs são estruturados com contexto.

5. **Separação entre lógica e efeitos colaterais**
   - Nenhum código de banco, envio de email ou integração externa dentro dos services diretamente.
   - Toda interação com o mundo externo é mediada por repositories ou adapters.

6. **Arquivos curtos e objetivos**
   - Cada arquivo tem um foco específico.
   - Quando um arquivo cresce demais, é dividido em múltiplos por função ou contexto.

#### Convenções e boas práticas adotadas
- PEP8: Estilo Python padronizado.
- Tipagem estática para validação de tipos.
- Comentários e docstrings são usados quando necessários.

O resultado é um backend que mantém o código limpo, modular, testável e sustentável, facilitando a manutenção, depuração e a adição de novas funcionalidades.