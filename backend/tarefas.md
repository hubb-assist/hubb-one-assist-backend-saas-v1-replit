# Tarefas do Projeto HUBB ONE Assist

## Módulo de Usuários

- [x] Criar modelo de dados para Usuário
- [x] Implementar esquemas Pydantic para validação
- [x] Criar serviço de usuários com operações CRUD
- [x] Implementar rotas REST para usuários
- [x] Adicionar funcionalidade de busca e filtros
- [x] Implementar paginação na listagem de usuários
- [x] Configurar validações e tratamento de erros
- [x] Adicionar endpoints específicos para ativar/desativar usuários (PATCH /users/{user_id}/activate, /users/{user_id}/deactivate)

## Módulo de Segmentos

- [x] Criar modelo de dados para Segmento com UUID, nome, descrição, is_active e timestamps
- [x] Implementar esquemas Pydantic para validação de entrada e saída
- [x] Criar serviço de segmentos com operações CRUD completas
- [x] Implementar rotas REST para segmentos (/segments/)
- [x] Configurar validações e tratamento de erros
- [x] Adicionar endpoints específicos para ativar/desativar segmentos (PATCH /segments/{segment_id}/activate, /segments/{segment_id}/deactivate)

## Módulo de Módulos Funcionais

- [x] Criar modelo de dados para Module com UUID, nome, descrição, is_active e timestamps
- [x] Implementar esquemas Pydantic para validação de entrada e saída
- [x] Criar serviço de módulos com operações CRUD completas
- [x] Implementar rotas REST para módulos (/modules/)
- [x] Configurar validações e tratamento de erros
- [x] Adicionar endpoints específicos para ativar/desativar módulos (PATCH /modules/{module_id}/activate, /modules/{module_id}/deactivate)

## Módulo de Planos

- [x] Criar modelo de dados para Plan e PlanModule com os campos especificados
- [x] Implementar relacionamento N-N entre planos e módulos com atributos adicionais (preço, gratuidade, dias de teste)
- [x] Implementar esquemas Pydantic para validação de entrada e saída
- [x] Criar serviço de planos com operações CRUD completas e regras de negócio
- [x] Implementar rotas REST para planos (/plans/)
- [x] Configurar validações e tratamento de erros
- [x] Adicionar endpoints específicos para ativar/desativar planos

## Configuração do Ambiente

- [x] Configurar adaptador ASGI para WSGI para compatibilidade com FastAPI/Uvicorn e Gunicorn
- [x] Configurar banco de dados PostgreSQL
- [x] Configurar estrutura de diretórios do projeto conforme arquitetura DDD
- [x] Documentar regras do projeto (rules.md)

## Integração e Segurança

- [x] Implementar autenticação JWT com cookies HttpOnly
- [x] Configurar proteção CORS para permitir a origem do frontend específico
- [x] Adicionar endpoint `/users/me` para obter usuário atual autenticado
- [x] Implementar refresh automático de tokens para manter sessão

✅ TAREFA BACKEND - CRUD de Planos (Plan) implementado com sucesso, incluindo associação com módulos
✅ TAREFA BACKEND - Configurado CORS para permitir requisições do frontend específico (https://977761fe-66ad-4e57-b1d5-f3356eb27515-00-1yp0n9cqd8r5p.spock.replit.dev)