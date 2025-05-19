# 📊 Padrões e Práticas de Domain Driven Design (DDD)

Este documento define os padrões, práticas e estruturas adotadas pelo sistema HUBB ONE Assist para implementação de **Domain Driven Design (DDD)**. O objetivo é garantir código de alta qualidade, expressivo e com regras de negócio encapsuladas adequadamente.

## 🏛️ Arquitetura em Camadas

O sistema HUBB ONE Assist implementa uma arquitetura em camadas seguindo os princípios DDD:

### 1. Camada de Interface (app/api)
- Rotas FastAPI
- Controllers
- Middlewares
- Apenas coordena fluxo entre requisição e casos de uso

### 2. Camada de Aplicação (app/application)
- Casos de uso que orquestram operações
- DTOs (schemas pydantic)
- Conversão entre formatos de dados
- Não contém regras de negócio complexas

### 3. Camada de Domínio (app/domain)
- Entidades de domínio ricas com comportamentos
- Value Objects para validação e formatação
- Interfaces de repositórios (abstrações)
- Serviços de domínio
- Contém toda a lógica de negócio

### 4. Camada de Infraestrutura (app/infrastructure)
- Implementações concretas de repositórios
- Adaptadores para ORM e APIs externas
- Configurações técnicas
- Não contém regras de negócio

## 💎 Value Objects

Os Value Objects são objetos imutáveis que representam conceitos do domínio que são identificados por seus atributos, não por identidade. São utilizados para validação, formatação e encapsulamento de regras de negócio específicas.

### CPF - Cadastro de Pessoa Física

```python
@dataclass(frozen=True)
class CPF:
    """
    Value Object para CPF.
    Esta classe imutável representa um CPF com validação e formatação.
    """
    value: str
    
    def __post_init__(self):
        """Validação do CPF ao instanciar o objeto."""
        if not self._is_valid():
            raise ValueError(f"CPF inválido: {self.value}")
```

#### Características do Value Object CPF:
- **Imutabilidade**: Uma vez criado, seus valores não podem ser alterados
- **Validação embutida**: Validação completa do algoritmo de CPF (dígitos verificadores)
- **Auto-validação**: Valida-se no momento da criação
- **Métodos para acesso**: Formatado (123.456.789-09) e não formatado (12345678909)
- **Tratamento para nulos**: Método `create()` que aceita valores nulos ou vazios

#### Exemplo de uso:
```python
# Criação direta (lança exceção se inválido)
cpf = CPF("123.456.789-09")

# Criação segura (retorna None se valor for nulo ou vazio)
cpf = CPF.create("123.456.789-09")
cpf = CPF.create(None)  # Retorna None

# Acesso formatado
str(cpf)  # "123.456.789-09"

# Acesso não formatado 
cpf.unformatted()  # "12345678909"
```

### Phone - Telefone

```python
@dataclass(frozen=True)
class Phone:
    """
    Value Object para telefone.
    Esta classe imutável representa um número de telefone com validação e formatação.
    """
    value: str
    
    def __post_init__(self):
        """Validação do telefone ao instanciar o objeto."""
        if not self._is_valid():
            raise ValueError(f"Telefone inválido: {self.value}")
```

#### Características do Value Object Phone:
- **Validação específica**: Validação de telefones brasileiros (fixos e celulares)
- **Regras de negócio**: Celulares devem começar com dígito 9, DDD entre 11-99
- **Formatação inteligente**: (11) 98765-4321 para celular ou (11) 2345-6789 para fixo
- **Métodos para acesso**: Formatado e não formatado (apenas números)

#### Exemplo de uso:
```python
# Criação com telefone celular
phone = Phone("11987654321")
str(phone)  # "(11) 98765-4321"

# Criação com telefone fixo
phone = Phone("1123456789")
str(phone)  # "(11) 2345-6789"
```

### Address - Endereço

```python
@dataclass(frozen=True)
class Address:
    """
    Value Object para endereço completo.
    Esta classe imutável representa um endereço com seus diversos componentes.
    """
    zip_code: Optional[str] = None
    street: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
```

#### Características do Value Object Address:
- **Validação de componentes**: CEP válido (8 dígitos), UF válida (estados brasileiros)
- **Verificação de completude**: Método `is_complete()` para verificar campos obrigatórios
- **Formatação padronizada**: Representação como string formatada para exibição
- **Normalização de dados**: Tratamento para valores vazios ou nulos

#### Exemplo de uso:
```python
# Criação de endereço completo
address = Address.create(
    zip_code="12345678",
    street="Rua das Flores",
    number="123",
    district="Centro",
    city="São Paulo",
    state="SP"
)

# Verificação de completude
address.is_complete()  # True

# Representação formatada
str(address)  # "Rua das Flores, 123, Centro, São Paulo-SP, 12345-678"
```

## 🧠 Entidades Ricas

As entidades são objetos que possuem identidade própria, persistem ao longo do tempo e encapsulam comportamentos relevantes do domínio. No HUBB ONE Assist, entidades ricas são implementadas utilizando Value Objects para validação de seus atributos.

### Exemplo: Entidade Patient

```python
class PatientEntity:
    """
    Entidade rica que representa um paciente no sistema.
    Utiliza Value Objects para garantir a validade dos dados essenciais.
    """
    def __init__(
        self,
        id: Optional[UUID] = None,
        name: str = "",
        cpf: str = "",
        # ... outros atributos
    ):
        self.id = id or uuid4()
        self.name = name.strip()
        
        # Value Objects para validação e formatação
        self._cpf = CPF.create(cpf)
        self._phone = Phone.create(phone)
        self._address = Address.create(...)
```

#### Características da Entidade Rica:
- **Identificador único**: UUID como identificador permanente
- **Encapsulamento de regras**: Validações embutidas via Value Objects
- **Comportamentos de domínio**: Métodos que expressam operações de negócio
- **Properties para acesso seguro**: Exposição controlada dos atributos

#### Comportamentos da Entidade Patient:
- **update_personal_info()**: Atualiza informações pessoais com validação
- **update_contact_info()**: Atualiza contatos com validação de telefone
- **update_address()**: Atualiza endereço completo com validação
- **deactivate()**: Desativa o paciente logicamente
- **activate()**: Reativa um paciente desativado

## 🔄 Adaptadores

Os adaptadores são responsáveis por converter entre as entidades de domínio ricas e os modelos simples de persistência (ORM) ou DTOs de API.

### Exemplo: PatientAdapter

```python
class PatientAdapter:
    """
    Classe adaptadora que converte entre PatientEntity (domínio) e Patient (ORM).
    """
    
    @staticmethod
    def to_entity(orm_model: Patient) -> Optional[PatientEntity]:
        # Converte modelo ORM para entidade de domínio
        
    @staticmethod
    def to_orm_model(entity: PatientEntity) -> Patient:
        # Converte entidade de domínio para modelo ORM
        
    @staticmethod
    def extract_simple_data(entity: PatientEntity) -> dict:
        # Extrai dados simples para serialização
```

## 🧪 Testes de Domínio

Testes específicos para as regras de domínio validam o comportamento das entidades e Value Objects independentemente de infraestrutura ou APIs.

### Testes para Value Objects

- Validação de dados válidos
- Validação de dados inválidos (exceções esperadas)
- Formatação correta
- Tratamento de valores nulos ou vazios

### Testes para Entidades

- Criação com Value Objects
- Validação em métodos de atualização
- Comportamentos de negócio específicos

## 📝 Diretrizes de Implementação

1. **Value Objects para validações**: Utilize Value Objects sempre que houver necessidade de validação específica ou formatação padronizada.

2. **Entidades com comportamentos**: Entidades devem expor métodos que representam operações permitidas no domínio, não apenas getters e setters.

3. **Imutabilidade quando possível**: Value Objects devem ser sempre imutáveis (frozen=True). Entidades podem ter estados que mudam.

4. **Adaptadores para conversão**: Sempre use adaptadores para isolar a camada de domínio da infraestrutura.

5. **Interfaces e inversão de dependência**: Use interfaces (classes abstratas) para repositórios e serviços externos.

## 📚 Referências

- Evans, Eric. "Domain-Driven Design: Tackling Complexity in the Heart of Software"
- Vernon, Vaughn. "Implementing Domain-Driven Design"
- Fowler, Martin. "Patterns of Enterprise Application Architecture"

## 📌 Última atualização

- Versão: `v1.0`
- Data: `2025-05-19`
- Responsável técnico: **Equipe de Desenvolvimento**