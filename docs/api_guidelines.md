# 📡 HUBB Assist — Diretrizes de API e Desenvolvimento

Este documento define os padrões, boas práticas e regras para o desenvolvimento e manutenção das APIs do sistema HUBB ONE Assist. Seu objetivo é garantir consistência, segurança e clareza nas interfaces de comunicação, prevenindo problemas comuns de desenvolvimento.

## 🌐 Domínios Oficiais do Sistema

- **API/Backend:** https://api.hubbassist.com
- **Frontend/App:** https://app.hubbassist.com

## 🎯 Contexto e Escopo do Sistema

O HUBB ONE Assist é uma plataforma SaaS multitenancy para gestão profissional de clínicas e consultórios, com foco inicial nos segmentos de Odontologia e Veterinária. É um sistema de gestão administrativa completo, **sem componentes de hardware ou dispositivos físicos**.

### 📋 Entidades Principais do Sistema

- **Usuários (Users)**: Pessoas que acessam o sistema, com diferentes perfis e permissões
- **Segmentos (Segments)**: Áreas de atuação profissional (ex: Odontologia, Veterinária)
- **Módulos (Modules)**: Funcionalidades do sistema que podem ser associadas a um plano
- **Planos (Plans)**: Pacotes de serviços oferecidos aos assinantes, com diferentes módulos
- **Assinantes (Subscribers)**: Clínicas ou consultórios que contratam o sistema

## 🚫 Regras de Escopo e Desenvolvimento

### 1. Princípio de Conformidade com o Escopo
- ✅ Todas as APIs devem estar alinhadas com o domínio de negócio do sistema (gestão de clínicas)
- ❌ NÃO implementar APIs para controle de dispositivos IoT, hardware, Arduino, ESP32, sensores, etc.
- ❌ NÃO desenvolver endpoints que não tenham relação direta com as entidades principais do sistema

### 2. Regras de Aprovação e Controle
- ✅ Toda nova API ou endpoint deve ser explicitamente solicitado e aprovado pelo responsável técnico
- ✅ Solicitações de API devem incluir justificativa clara, casos de uso e valor para o negócio
- ❌ NÃO criar APIs experimentais, de teste ou "extras" sem aprovação formal
- ❌ NÃO implementar recursos técnicos complexos por iniciativa própria (message queues, websockets, etc.)

### 3. Critérios de Segurança e Acesso
- ✅ Endpoints protegidos devem validar JWT e aplicar filtros por subscriber_id (isolamento multitenancy)
- ✅ Endpoints públicos devem ser claramente documentados e passar por revisão de segurança
- ❌ NÃO expor endpoints que permitam acesso sem controle adequado a dados críticos
- ❌ NÃO implementar bypass de autenticação, mesmo para testes ou "para facilitar desenvolvimento"

## 🔧 Estrutura e Nomenclatura

### Estrutura de Rotas
- ✅ Endpoints protegidos por autenticação: `/{recurso}/` (ex: `/users/`, `/plans/`)
- ✅ Endpoints públicos (sem autenticação): `/public/{recurso}/` (ex: `/public/plans/`)
- ✅ Utilizar plurais para coleções e verbos HTTP apropriados (GET, POST, PUT, DELETE, PATCH)

### Convenção de Nomenclatura
- Arquivos de rotas: `routes_{recurso}.py` (ex: `routes_subscribers.py`)
- Arquivos de rotas públicas: `routes_public_{recurso}.py` (ex: `routes_public_plans.py`)
- Schemas: `{recurso}.py` (ex: `subscriber.py`)
- Services: `{recurso}_service.py` (ex: `subscriber_service.py`)

## 📨 Formato de Requisições e Respostas

### 1. JSON como Padrão
- Todas as APIs devem aceitar e retornar JSON como formato padrão
- Utilizar snake_case para nomes de propriedades em JSON (ex: `first_name`, `is_active`)

### 2. Paginação Padronizada
```json
{
  "total": 100,
  "page": 1,
  "size": 10,
  "items": [...]
}
```

### 3. Respostas de Erro
```json
{
  "detail": "Mensagem de erro específica"
}
```

## 🛡️ Segurança e Autenticação

### 1. Autenticação por JWT em Cookies HttpOnly
- Todas as APIs protegidas exigem token JWT válido em cookie HttpOnly
- Tokens devem incluir `user_id`, `role`, `subscriber_id` e `permissions`
- Cookies configurados com `Secure=True` e `SameSite="none"` para CORS

### 2. CORS Configurado Corretamente
- Origens permitidas configuradas em ambiente via variáveis
- Credentials habilitadas para uso com cookies
- Frontend deve usar `credentials: "include"` ou `withCredentials: true`

## 🏢 Arquitetura Multitenancy

### 1. Isolamento por Subscriber_ID
- Todas as entidades relevantes para o negócio devem ter campo `subscriber_id`
- Filtro automático por `subscriber_id` em consultas para garantir isolamento de dados
- Usuários com role `SUPER_ADMIN` e `DIRETOR` podem ver todos os registros

### 2. Acesso por Hierarquia
```
SUPER_ADMIN: Acesso completo a todos os dados e recursos
DIRETOR: Acesso à gestão de assinantes e dados administrativos
COLABORADOR: Acesso às operações dentro do seu assinante
DONO_ASSINANTE: Acesso à gestão do próprio assinante (clínica)
```

## 🏗️ Exemplos de Implementação

### 1. Endpoint Protegido com Filtro de Assinante
```python
@router.get("/subscribers/", response_model=PaginatedResponse[SubscriberResponse])
async def list_subscribers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None)
):
    filter_params = {"name": name} if name else {}
    return SubscriberService.get_subscribers(
        db, current_user, skip=skip, limit=limit, filter_params=filter_params
    )
```

### 2. Endpoint Público
```python
@router_public.post("/public/subscribers/", response_model=SubscriberCreateResponse)
async def create_subscriber(
    subscriber_data: SubscriberCreate,
    db: Session = Depends(get_db)
):
    return SubscriberService.create_subscriber(db, subscriber_data)
```

## 🚨 Lições Aprendidas e Armadilhas Comuns

### 1. Parâmetros em Ordem Correta
- Sempre verifique a ordem dos parâmetros ao chamar funções
- Problema encontrado: Inversão de parâmetros na função `apply_subscriber_filter`
- Solução: Corrigir a ordem dos parâmetros: `query, current_user, Subscriber`

### 2. Erro 404 em Rotas
- O frontend deve usar a rota correta para acessar os endpoints
- Problema encontrado: Frontend tentando acessar `/external-api/subscribers` (não existente)
- Solução: Usar a rota correta: `/subscribers/`

### 3. Inclusão de Credenciais em Requisições
- O frontend deve incluir `credentials: "include"` em todas as requisições
- Problema comum: CORS bloqueando cookies por falta de configuração adequada

## 📝 Processos de Mudança

### 1. Proposta de Novo Endpoint
Para solicitar um novo endpoint ou API:

1. Descrever claramente o propósito e valor para o negócio
2. Identificar as entidades e relacionamentos envolvidos
3. Especificar os métodos HTTP e estrutura de dados
4. Receber aprovação explícita antes de implementar

### 2. Checklist de Revisão
- O endpoint está alinhado com o escopo do sistema?
- A segurança e autenticação estão implementadas corretamente?
- O isolamento multitenancy está respeitado?
- A documentação e testes são adequados?

## 📌 Última atualização

- Versão: `v1.0`
- Data: `2025-05-12`
- Responsável técnico: **Luis Paim**