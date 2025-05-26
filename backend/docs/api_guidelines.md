# Guia de Boas Práticas API - HUBB ONE Assist

## Arquitetura DDD (Domain-Driven Design) 

Este documento detalha a arquitetura e as diretrizes seguidas na implementação dos módulos do sistema, exemplificando com o módulo de Agendamentos (Appointments).

### Princípios DDD Implementados

#### 1. Estrutura em Camadas

Nossa API segue uma estrutura em camadas que separa claramente as responsabilidades:

- **Camada de Domínio**: Entidades ricas com regras de negócio e interfaces de repositório
- **Camada de Aplicação**: Casos de uso que orquestram operações
- **Camada de Infraestrutura**: Implementações concretas de repositórios e serviços externos
- **Camada de Apresentação**: API REST com validação e tratamento de erros

#### 2. Entidades Ricas vs. Anêmicas

Nossas entidades de domínio implementam comportamentos e regras de negócio, não apenas armazenam dados.

Exemplo da entidade `Appointment`:

```python
class Appointment:
    def __init__(self, subscriber_id, patient_id, provider_id, ...):
        # Atributos inicializados
        # ...
        # Validação das regras de negócio na criação
        self._validate()
    
    def _validate(self) -> None:
        # Regras de validação encapsuladas na entidade
        if self.end_time <= self.start_time:
            raise ValueError("A data/hora de término deve ser posterior à data/hora de início")
        
    def cancel(self) -> None:
        # Lógica de negócio encapsulada em métodos
        if self.status == "completed":
            raise ValueError("Não é possível cancelar um agendamento já concluído")
        
        self.status = "cancelled"
        self.updated_at = datetime.utcnow()
```

#### 3. Interfaces e Inversão de Dependência

Definimos interfaces para repositórios, permitindo trocar implementações sem alterar o código de negócio.

```python
# Interface abstrata
class IAppointmentRepository(ABC):
    @abstractmethod
    def create(self, appointment: Appointment) -> Appointment:
        pass
    
    @abstractmethod
    def get_by_id(self, appointment_id: UUID, subscriber_id: UUID) -> Appointment:
        pass
    
    # Outros métodos...
```

#### 4. Casos de Uso

Cada operação é implementada como um caso de uso específico, seguindo o princípio de responsabilidade única.

```python
class CreateAppointmentUseCase:
    def __init__(self, repository: IAppointmentRepository):
        self.repository = repository
    
    def execute(self, data: Dict[str, Any], subscriber_id: UUID) -> Dict[str, Any]:
        # Lógica de aplicação para criar um agendamento
```

## Diretrizes de API REST

### 1. Nomenclatura de Rotas

- Use substantivos no plural para recursos: `/agendamentos`, `/pacientes`
- Evite verbos nas URLs - use métodos HTTP para indicar ações
- Use kebab-case para multi-palavras: `/custos-fixos`

### 2. Métodos HTTP e Semântica

| Método HTTP | Uso                                     | Exemplo                                      |
|-------------|----------------------------------------|----------------------------------------------|
| GET         | Recuperar recursos                     | `GET /agendamentos` - listar agendamentos    |
| POST        | Criar recursos                         | `POST /agendamentos` - criar agendamento     |
| PUT         | Atualizar recursos (completo)          | `PUT /agendamentos/{id}` - atualizar totalmente |
| PATCH       | Atualizar recursos (parcial)           | `PATCH /agendamentos/{id}` - atualizar parcialmente |
| DELETE      | Excluir recursos (logicamente)         | `DELETE /agendamentos/{id}` - excluir      |

### 3. Respostas e Códigos HTTP

| Código | Uso                                          |
|--------|----------------------------------------------|
| 200    | Sucesso em operações GET, PUT, PATCH         |
| 201    | Sucesso em operações POST (recurso criado)   |
| 204    | Sucesso em operações DELETE (sem conteúdo)   |
| 400    | Erro de validação, dados inválidos           |
| 401    | Autenticação necessária                      |
| 403    | Permissão negada (autenticado, mas sem acesso) |
| 404    | Recurso não encontrado                       |
| 500    | Erro interno do servidor                     |

### 4. Segurança Multi-tenant

Todos os endpoints devem implementar segurança multi-tenant:

```python
# Verificação de segurança multi-tenant - usuário deve ter um subscriber_id
if not hasattr(current_user, 'subscriber_id') or not current_user.subscriber_id:
    raise HTTPException(
        status_code=403,
        detail="O usuário não está associado a um assinante"
    )
```

## Implementação de Funcionalidades

### 1. Exclusão Lógica vs. Física

- Use exclusão lógica (soft delete) com campo `is_active` em vez de remoção física dos registros
- Implemente através do método `deactivate()` na entidade

### 2. Filtros e Paginação

- Sempre implemente paginação em endpoints que retornam listas
- Suporte parâmetros de consulta para filtrar recursos

```python
@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    patient_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    # ...
):
```

### 3. Validação de Dados

- Use Pydantic para validação de dados de entrada e saída
- Implemente validações de negócio nas entidades de domínio
- Combine validações na API e no domínio para integridade total

```python
class AppointmentBase(BaseModel):
    # Campos com validação
    service_name: str = Field(..., min_length=3, max_length=255)
    start_time: datetime
    end_time: datetime
    
    @validator("end_time")
    def end_time_after_start_time(cls, v, values):
        # Validação adicional
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("A data/hora de término deve ser posterior à data/hora de início")
        return v
```

## Exemplos de Implementação DDD

### 1. Estrutura de Arquivos Exemplo - Módulo de Agendamentos

```
app/
├── api/
│   └── routes/
│       └── appointment_router.py     # Rotas da API
├── application/
│   └── use_cases/
│       └── appointment_use_cases.py  # Casos de uso
├── domain/
│   └── appointment/
│       ├── entities.py               # Entidade de domínio
│       └── interfaces.py             # Interfaces (repositório)
├── infrastructure/
│   └── repositories/
│       └── appointment_sqlalchemy.py # Implementação do repositório
├── db/
│   └── models_appointment.py         # Modelo SQLAlchemy
└── schemas/
    └── appointment_schema.py         # Esquemas Pydantic
```

### 2. Fluxo de Dados entre Camadas

1. **API recebe requisição**
   - Valida dados com Pydantic
   - Obtém usuário autenticado
   - Verifica segurança multi-tenant

2. **API chama caso de uso**
   - Passa dados validados e dependências

3. **Caso de uso executa lógica de aplicação**
   - Cria/busca entidades de domínio
   - Chama métodos de domínio para operações

4. **Repositório persiste mudanças**
   - Converte entidades para modelos de BD
   - Executa operações no banco de dados

5. **API retorna resposta formatada**
   - Converte resultado para esquema de resposta
   - Define código HTTP e cabeçalhos adequados

### 3. Boas Práticas DDD Adicionais

- **Ubiquitous Language**: Use uma linguagem consistente em todos os componentes
- **Bounded Contexts**: Separe módulos com contextos de negócio distintos
- **Value Objects**: Para conceitos imutáveis do domínio (ex: Email, CPF)
- **Domain Events**: Para notificar mudanças significativas nas entidades
- **Agregados**: Identifique grupos de entidades que devem ser tratadas como uma unidade

## Implementação de Módulo Financeiro

O módulo Financeiro foi implementado seguindo rigorosamente os princípios de DDD apresentados neste documento, com o objetivo de gerenciar contas a pagar, contas a receber, fluxo de caixa e cálculo de lucro.

### 1. Estrutura de Arquivos - Módulo Financeiro

```
app/
├── api/
│   └── routes/
│       └── finance_router.py             # Rotas da API para o módulo Financeiro
├── application/
│   └── use_cases/
│       └── finance_use_cases.py          # Casos de uso para operações financeiras
├── domain/
│   └── finance/
│       ├── entities.py                   # Entidades de domínio (Payable, Receivable, ValueObjects)
│       └── interfaces.py                 # Interface do repositório financeiro
├── infrastructure/
│   └── repositories/
│       └── finance_sqlalchemy.py         # Implementação do repositório
├── db/
│   ├── models_payable.py                 # Modelo SQLAlchemy para contas a pagar
│   └── models_receivable.py              # Modelo SQLAlchemy para contas a receber
└── schemas/
    └── finance_schema.py                 # Esquemas Pydantic para validação
```

### 2. Entidades e Value Objects

O módulo implementa duas entidades principais e dois value objects:

- **PayableEntity**: Entidade para contas a pagar (obrigações financeiras)
- **ReceivableEntity**: Entidade para contas a receber (direitos creditórios)
- **CashFlowSummary (Value Object)**: Representa o sumário de fluxo de caixa em um período
- **ProfitCalculation (Value Object)**: Representa o cálculo de lucro com base em receitas e custos

### 3. Interface do Repositório

Interface `IFinanceRepository` define os seguintes métodos:

```python
class IFinanceRepository(ABC):
    # Métodos para Payables
    @abstractmethod
    def create_payable(self, data: PayableCreate, subscriber_id: UUID) -> PayableEntity:
        pass
    
    @abstractmethod
    def get_payable(self, id: UUID, subscriber_id: UUID) -> Optional[PayableEntity]:
        pass
    
    # ... outros métodos para Payables ...
    
    # Métodos para Receivables
    @abstractmethod
    def create_receivable(self, data: ReceivableCreate, subscriber_id: UUID) -> ReceivableEntity:
        pass
    
    # ... outros métodos para Receivables ...
    
    # Métodos para CashFlow e Profit
    @abstractmethod
    def get_cashflow(self, subscriber_id: UUID, from_date: date, to_date: date) -> CashFlowSummary:
        pass
    
    @abstractmethod
    def calculate_profit(self, subscriber_id: UUID, period_from: date, period_to: date) -> ProfitCalculation:
        pass
```

### 4. Casos de Uso

Os casos de uso implementados incluem:

- **CreatePayableUseCase**: Cria uma nova conta a pagar
- **GetPayableUseCase**: Busca uma conta a pagar pelo ID
- **ListPayablesUseCase**: Lista contas a pagar com filtros
- **UpdatePayableUseCase**: Atualiza uma conta a pagar existente
- **DeletePayableUseCase**: Exclui (logicamente) uma conta a pagar
- **Casos equivalentes para Receivables**
- **GetCashFlowUseCase**: Calcula o fluxo de caixa em um período
- **CalculateProfitUseCase**: Calcula lucro baseado em receitas e custos

### 5. Endpoints da API

A API expõe as seguintes rotas principais:

| Método HTTP | Endpoint                    | Descrição                                    |
|-------------|-----------------------------|--------------------------------------------|
| POST        | /finance/payables           | Criar uma nova conta a pagar                |
| GET         | /finance/payables/{id}      | Obter detalhes de uma conta a pagar         |
| GET         | /finance/payables           | Listar contas a pagar com filtros           |
| PUT         | /finance/payables/{id}      | Atualizar uma conta a pagar                 |
| DELETE      | /finance/payables/{id}      | Excluir uma conta a pagar                   |
| POST        | /finance/receivables        | Criar uma nova conta a receber              |
| GET         | /finance/receivables/{id}   | Obter detalhes de uma conta a receber       |
| GET         | /finance/receivables        | Listar contas a receber com filtros         |
| PUT         | /finance/receivables/{id}   | Atualizar uma conta a receber               |
| DELETE      | /finance/receivables/{id}   | Excluir uma conta a receber                 |
| GET         | /finance/cashflow           | Calcular fluxo de caixa em um período       |
| GET         | /finance/profit             | Calcular lucro em um período                |

### 6. Segurança e Validação

- Todas as rotas implementam segurança multi-tenant via `subscriber_id`
- Validação com Pydantic para todos os dados de entrada
- Validação adicional nas entidades de domínio
- Tratamento adequado de erros com códigos HTTP específicos

### 7. Integração com Módulo de Custos

O cálculo de lucro (`CalculateProfitUseCase`) integra-se com os módulos de Custos:

- Custos Fixos
- Custos Variáveis
- Custos Clínicos

Esta integração permite um cálculo preciso de lucro com base em todas as despesas registradas no sistema.

## Implementação de Módulo de Anamnese

O módulo de Anamnese foi implementado seguindo a arquitetura DDD para gerenciar o histórico médico dos pacientes, incluindo queixas principais, histórico médico, alergias, medicações e observações clínicas.

### 1. Estrutura de Arquivos - Módulo de Anamnese

```
app/
├── api/
│   └── routes/
│       └── anamnesis_router.py          # Rotas da API para Anamnese (aninhado em /patients/{id}/anamneses)
├── application/
│   └── use_cases/
│       └── anamnesis_use_cases.py       # Casos de uso para operações de anamnese
├── domain/
│   └── anamnesis/
│       ├── entities.py                  # Entidade de domínio AnamnesisEntity
│       └── interfaces.py                # Interface IAnamnesisRepository
├── infrastructure/
│   └── repositories/
│       └── anamnesis_sqlalchemy.py      # Implementação do repositório
├── db/
│   └── models_anamnesis.py              # Modelo SQLAlchemy para anamnese
└── schemas/
    └── anamnesis_schema.py              # Esquemas Pydantic para validação
```

### 2. Entidade de Domínio

A entidade `AnamnesisEntity` implementa a lógica de negócio para anamneses:

```python
class AnamnesisEntity:
    def __init__(
        self,
        id: Optional[UUID] = None,
        subscriber_id: Optional[UUID] = None,
        patient_id: Optional[UUID] = None,
        chief_complaint: Optional[str] = None,
        medical_history: Optional[str] = None,
        allergies: Optional[str] = None,
        medications: Optional[str] = None,
        notes: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        # Atributos inicializados
        self.id = id
        self.subscriber_id = subscriber_id
        self.patient_id = patient_id
        self.chief_complaint = chief_complaint
        self.medical_history = medical_history
        self.allergies = allergies
        self.medications = medications
        self.notes = notes
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        
        # Validação das regras de negócio na criação
        self._validate()
    
    def _validate(self) -> None:
        """Validações de regras de negócio"""
        if self.chief_complaint is None or len(self.chief_complaint.strip()) < 3:
            raise ValueError("A queixa principal é obrigatória e deve ter pelo menos 3 caracteres")
        
        if self.subscriber_id is None:
            raise ValueError("O ID do assinante é obrigatório")
            
        if self.patient_id is None:
            raise ValueError("O ID do paciente é obrigatório")
```

### 3. Interface do Repositório

A interface `IAnamnesisRepository` define os métodos necessários para manipular anamneses:

```python
class IAnamnesisRepository(ABC):
    @abstractmethod
    def create(self, data: AnamnesisCreate, patient_id: UUID, subscriber_id: UUID) -> AnamnesisEntity:
        pass
    
    @abstractmethod
    def get_by_id(self, id: UUID, subscriber_id: UUID) -> Optional[AnamnesisEntity]:
        pass
    
    @abstractmethod
    def list_by_patient(
        self, patient_id: UUID, subscriber_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AnamnesisEntity]:
        pass
    
    @abstractmethod
    def update(self, id: UUID, data: AnamnesisUpdate, subscriber_id: UUID) -> Optional[AnamnesisEntity]:
        pass
    
    @abstractmethod
    def delete(self, id: UUID, subscriber_id: UUID) -> bool:
        pass
    
    @abstractmethod
    def count_by_patient(self, patient_id: UUID, subscriber_id: UUID) -> int:
        pass
```

### 4. Casos de Uso

O módulo implementa os seguintes casos de uso:

- **CreateAnamnesisUseCase**: Cria uma nova ficha de anamnese para um paciente
- **GetAnamnesisUseCase**: Busca uma anamnese específica pelo ID
- **ListAnamnesisUseCase**: Lista as anamneses de um paciente com paginação
- **UpdateAnamnesisUseCase**: Atualiza uma anamnese existente
- **DeleteAnamnesisUseCase**: Exclui (logicamente) uma anamnese

Exemplo de implementação:

```python
class CreateAnamnesisUseCase:
    def __init__(self, repository: IAnamnesisRepository):
        self.repository = repository
    
    def execute(self, data: AnamnesisCreate, patient_id: UUID, subscriber_id: UUID) -> Dict[str, Any]:
        try:
            anamnesis_entity = self.repository.create(data, patient_id, subscriber_id)
            return anamnesis_entity.to_dict()
        except Exception as e:
            raise ValueError(f"Erro ao criar anamnese: {str(e)}")
```

### 5. Schemas Pydantic

Os schemas Pydantic usados para validação:

- **AnamnesisBase**: Schema base com campos comuns
- **AnamnesisCreate**: Schema para criação
- **AnamnesisUpdate**: Schema para atualização (campos opcionais)
- **AnamnesisResponse**: Schema para resposta
- **AnamnesisListResponse**: Schema para listagem com paginação

```python
class AnamnesisBase(BaseModel):
    chief_complaint: str = Field(..., min_length=3, description="Queixa principal do paciente")
    medical_history: Optional[str] = Field(None, description="Histórico médico do paciente")
    allergies: Optional[str] = Field(None, description="Lista de alergias do paciente")
    medications: Optional[str] = Field(None, description="Medicamentos que o paciente está tomando")
    notes: Optional[str] = Field(None, description="Observações adicionais")
```

### 6. Endpoints da API

A API expõe as seguintes rotas (aninhadas sob `/patients/{patient_id}/anamneses`):

| Método HTTP | Endpoint                             | Descrição                               |
|-------------|------------------------------------- |----------------------------------------|
| POST        | /patients/{id}/anamneses/            | Criar uma nova anamnese                |
| GET         | /patients/{id}/anamneses/{anam_id}   | Obter detalhes de uma anamnese         |
| GET         | /patients/{id}/anamneses/            | Listar anamneses do paciente           |
| PUT         | /patients/{id}/anamneses/{anam_id}   | Atualizar uma anamnese                 |
| DELETE      | /patients/{id}/anamneses/{anam_id}   | Excluir uma anamnese (exclusão lógica) |

### 7. Segurança e Validação

- Todas as rotas implementam segurança multi-tenant via `subscriber_id`
- Validação dupla: Pydantic na API e lógica de negócio na entidade
- Testes confirmam o funcionamento adequado dos endpoints:
  - Criar (POST): 201 Created - Retorna o objeto criado
  - Listar (GET): 200 OK - Retorna itens paginados com total
  - Obter (GET): 200 OK - Retorna detalhes completos da anamnese
  - Atualizar (PUT): 200 OK - Retorna objeto atualizado
  - Excluir (DELETE): 204 No Content - Indica exclusão bem-sucedida

### 8. Integração com Módulo de Pacientes

O módulo de Anamnese integra-se diretamente com o módulo de Pacientes:

- As anamneses são sempre associadas a um paciente específico
- As rotas são aninhadas (nested routes) sob o recurso de pacientes
- A segurança verifica se a anamnese pertence ao paciente indicado na URL

## Conclusão

Siga estas diretrizes ao implementar novos módulos ou modificar os existentes para garantir:

- Código consistente e de alta qualidade
- Separação clara de responsabilidades
- Facilidade de manutenção e evolução
- Testabilidade em todos os níveis
- Segurança multi-tenant por design

---

**Autores:** Equipe de Desenvolvimento HUBB ONE Assist
**Última atualização:** 20 de Maio de 2025