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

## 🏷️ Módulo de Gerenciamento de Custos

### 1. Custos Fixos
#### 1.1 Listar Custos Fixos
```python
@router.get("/custos/fixos/", response_model=PaginatedResponse[CustoFixoResponse])
async def list_custos_fixos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    nome: Optional[str] = Query(None)
):
    """
    Lista custos fixos com filtros opcionais por data e nome.
    Requer autenticação e aplica filtro por subscriber_id.
    """
```

#### 1.2 Criar Custo Fixo
```python
@router.post("/custos/fixos/", response_model=CustoFixoResponse)
async def create_custo_fixo(
    data: CustoFixoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo custo fixo.
    Requer autenticação e associa ao subscriber_id do usuário atual.
    """
```

#### 1.3 Obter Custo Fixo por ID
```python
@router.get("/custos/fixos/{custo_id}", response_model=CustoFixoResponse)
async def get_custo_fixo(
    custo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna detalhes de um custo fixo específico por ID.
    Requer autenticação e verifica se o custo pertence ao subscriber do usuário.
    """
```

#### 1.4 Atualizar Custo Fixo
```python
@router.put("/custos/fixos/{custo_id}", response_model=CustoFixoResponse)
async def update_custo_fixo(
    custo_id: UUID,
    data: CustoFixoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um custo fixo existente.
    Requer autenticação e verifica permissões de acesso.
    """
```

#### 1.5 Excluir Custo Fixo (desativação lógica)
```python
@router.delete("/custos/fixos/{custo_id}", response_model=GenericResponse)
async def delete_custo_fixo(
    custo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Desativa logicamente um custo fixo (não remove do banco).
    Requer autenticação e verifica permissões de acesso.
    """
```

### 2. Custos Variáveis
#### 2.1 Listar Custos Variáveis
```python
@router.get("/custos/variaveis/", response_model=PaginatedResponse[CustoVariavelResponse])
async def list_custos_variaveis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    nome: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None)
):
    """
    Lista custos variáveis com filtros opcionais por data, nome e categoria.
    Requer autenticação e aplica filtro por subscriber_id.
    """
```

#### 2.2 Criar Custo Variável
```python
@router.post("/custos/variaveis/", response_model=CustoVariavelResponse)
async def create_custo_variavel(
    data: CustoVariavelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo custo variável.
    Requer autenticação e associa ao subscriber_id do usuário atual.
    """
```

#### 2.3 Obter Custo Variável por ID
```python
@router.get("/custos/variaveis/{custo_id}", response_model=CustoVariavelResponse)
async def get_custo_variavel(
    custo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna detalhes de um custo variável específico por ID.
    Requer autenticação e verifica se o custo pertence ao subscriber do usuário.
    """
```

#### 2.4 Atualizar Custo Variável
```python
@router.put("/custos/variaveis/{custo_id}", response_model=CustoVariavelResponse)
async def update_custo_variavel(
    custo_id: UUID,
    data: CustoVariavelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um custo variável existente.
    Requer autenticação e verifica permissões de acesso.
    """
```

#### 2.5 Excluir Custo Variável (desativação lógica)
```python
@router.delete("/custos/variaveis/{custo_id}", response_model=GenericResponse)
async def delete_custo_variavel(
    custo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Desativa logicamente um custo variável (não remove do banco).
    Requer autenticação e verifica permissões de acesso.
    """
```

### 3. Custos Clínicos (Implementação DDD)
#### 3.1 Listar Custos Clínicos
```python
@router.get("/custos/clinicos/", response_model=PaginatedResponse[CustoClinicoResponse])
async def list_custos_clinicos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    repository = Depends(cost_clinical_repository_factory),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    procedure_name: Optional[str] = Query(None)
):
    """
    Lista custos clínicos com filtros opcionais.
    Implementa arquitetura DDD com injeção de dependência do repositório.
    """
```

#### 3.2 Criar Custo Clínico
```python
@router.post("/custos/clinicos/", response_model=CustoClinicoResponse)
async def create_custo_clinico(
    data: CustoClinicoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    repository = Depends(cost_clinical_repository_factory)
):
    """
    Cria um novo custo clínico.
    Utiliza padrão Use Case para encapsular a lógica de negócio.
    """
```

#### 3.3 Obter Custo Clínico por ID
```python
@router.get("/custos/clinicos/{custo_id}", response_model=CustoClinicoResponse)
async def get_custo_clinico(
    custo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    repository = Depends(cost_clinical_repository_factory)
):
    """
    Retorna detalhes de um custo clínico específico.
    Implementa padrão DDD com domínio rico.
    """
```

#### 3.4 Atualizar Custo Clínico
```python
@router.put("/custos/clinicos/{custo_id}", response_model=CustoClinicoResponse)
async def update_custo_clinico(
    custo_id: UUID,
    data: CustoClinicoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    repository = Depends(cost_clinical_repository_factory)
):
    """
    Atualiza um custo clínico existente.
    Utiliza casos de uso isolados para cada operação.
    """
```

#### 3.5 Excluir Custo Clínico
```python
@router.delete("/custos/clinicos/{custo_id}", response_model=GenericResponse)
async def delete_custo_clinico(
    custo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    repository = Depends(cost_clinical_repository_factory)
):
    """
    Desativa logicamente um custo clínico.
    Usa padrão Repository para persistência.
    """
```

### 4. Insumos (Módulo de Suprimentos)
#### 4.1 Listar Insumos
```python
@router.get("/insumos/", response_model=PaginatedResponse[InsumoResponse])
async def list_insumos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    nome: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    estoque_minimo: Optional[bool] = Query(None)
):
    """
    Lista insumos com filtros opcionais.
    Inclui opção para filtrar itens abaixo do estoque mínimo.
    """
```

#### 4.2 Criar Insumo
```python
@router.post("/insumos/", response_model=InsumoResponse)
async def create_insumo(
    data: InsumoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo insumo no sistema.
    Inclui validações de dados via Pydantic.
    """
```

#### 4.3 Obter Insumo por ID
```python
@router.get("/insumos/{insumo_id}", response_model=InsumoResponse)
async def get_insumo(
    insumo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna detalhes completos de um insumo.
    Inclui dados de estoque atual e mínimo.
    """
```

#### 4.4 Atualizar Insumo
```python
@router.put("/insumos/{insumo_id}", response_model=InsumoResponse)
async def update_insumo(
    insumo_id: UUID,
    data: InsumoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza dados de um insumo existente.
    Permite atualização parcial via modelo Pydantic.
    """
```

#### 4.5 Atualizar Estoque de Insumo
```python
@router.post("/insumos/{insumo_id}/estoque", response_model=InsumoResponse)
async def update_estoque_insumo(
    insumo_id: UUID,
    data: EstoqueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza o estoque de um insumo (entrada ou saída).
    Registra movimentação com data, quantidade e valor unitário.
    """
```

### 5. Relatórios de Custos (Consolidação)
#### 5.1 Gerar Relatório de Custos
```python
@router.post("/relatorios/custos/", response_model=RelatorioCustosResponse)
async def gerar_relatorio_custos(
    data: RelatorioCustosCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gera um relatório consolidado de custos.
    Inclui custos fixos, variáveis, clínicos e insumos.
    Permite filtros por período e tipo de relatório.
    """
```

#### 5.2 Listar Relatórios Salvos
```python
@router.get("/relatorios/custos/", response_model=PaginatedResponse[RelatorioCustosResponse])
async def list_relatorios_custos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    tipo_relatorio: Optional[ReportTypeEnum] = Query(None)
):
    """
    Lista relatórios salvos anteriormente.
    Permite filtros por data e tipo de relatório.
    """
```

#### 5.3 Obter Relatório por ID
```python
@router.get("/relatorios/custos/{relatorio_id}", response_model=RelatorioCustosDetalhesResponse)
async def get_relatorio_custos(
    relatorio_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna detalhes completos de um relatório salvo.
    Inclui todos os custos categorizados e totalizados.
    """
```

#### 5.4 Gerar Análise de Evolução de Custos
```python
@router.get("/relatorios/custos/evolucao", response_model=EvolucaoMensalResponse)
async def get_evolucao_custos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ano: int = Query(..., description="Ano para análise"),
    tipo_custo: Optional[TipoCustoEnum] = Query(None, description="Tipo de custo para filtrar")
):
    """
    Gera análise de evolução mensal de custos.
    Retorna dados mensais para visualização em gráficos.
    """
```

#### 5.5 Calcular Distribuição Percentual de Custos
```python
@router.get("/relatorios/custos/distribuicao", response_model=DistribuicaoCustosResponse)
async def get_distribuicao_custos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    date_from: date = Query(...),
    date_to: date = Query(...)
):
    """
    Calcula a distribuição percentual de custos por categoria.
    Útil para visualização em gráficos de pizza/rosca.
    """
```

## 📚 Exemplos de Requisições e Respostas

### 1. Criação de Custo Clínico (Request)
```json
POST /custos/clinicos/
{
  "procedure_name": "Consulta Odontológica",
  "duration_hours": 1.5,
  "hourly_rate": 120.00,
  "date": "2025-05-20",
  "observacoes": "Consulta de avaliação inicial"
}
```

### 2. Resposta de Custo Clínico Criado
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "procedure_name": "Consulta Odontológica",
  "duration_hours": 1.5,
  "hourly_rate": 120.00,
  "total_cost": 180.00,
  "date": "2025-05-20",
  "subscriber_id": "98765432-abcd-1234-efgh-456789abcdef",
  "observacoes": "Consulta de avaliação inicial",
  "is_active": true,
  "created_at": "2025-05-20T14:30:25.123Z",
  "updated_at": "2025-05-20T14:30:25.123Z"
}
```

### 3. Atualização de Estoque de Insumo (Request)
```json
POST /insumos/a1b2c3d4-e5f6-7890-abcd-ef1234567890/estoque
{
  "tipo_movimento": "entrada",
  "quantidade": 10,
  "valor_unitario": 25.50,
  "observacoes": "Reposição de estoque"
}
```

### 4. Geração de Relatório de Custos (Request)
```json
POST /relatorios/custos/
{
  "date_from": "2025-01-01",
  "date_to": "2025-05-31",
  "tipo_relatorio": "MENSAL",
  "titulo": "Relatório de Custos - 1º Semestre/2025",
  "incluir_detalhes": true
}
```

### 5. Resposta de Relatório de Custos (Resumo)
```json
{
  "id": "f1e2d3c4-b5a6-7890-abcd-ef1234567890",
  "titulo": "Relatório de Custos - 1º Semestre/2025",
  "date_from": "2025-01-01",
  "date_to": "2025-05-31",
  "tipo_relatorio": "MENSAL",
  "total_fixed_costs": 25000.00,
  "total_variable_costs": 18750.50,
  "total_clinical_costs": 42300.00,
  "total_supplies_costs": 8450.75,
  "grand_total": 94501.25,
  "distribuicao_percentual": {
    "fixos": 26.45,
    "variaveis": 19.84,
    "clinicos": 44.76,
    "insumos": 8.94
  },
  "created_at": "2025-05-20T15:10:45.789Z"
}
```

## 📌 Última atualização

- Versão: `v1.1`
- Data: `2025-05-20`
- Responsável técnico: **Luis Paim**