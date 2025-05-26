# Guia de Compatibilidade com Pydantic v2

## Problema Encontrado
O deployment estava falhando com o erro:
```
PydanticUserError: `regex` is removed. use `pattern` instead
```

Este erro era causado por incompatibilidades com a versão 2 do Pydantic, que removeu o parâmetro `regex` em favor de `pattern` e alterou a forma como os validadores são definidos.

## Solução Implementada

1. **Atualizamos o schema de validação em `app/schemas/insumo.py`**:
   - Substituímos `validator` por `field_validator` (Pydantic v2)
   - Adicionamos tipos de retorno explícitos aos validadores
   - Corrigimos a implementação da classe `InsumoResponse` para evitar conflitos de herança
   - Mantivemos o uso de `pattern` em vez de `regex` (que foi depreciado)
   - Ajustamos definições de tipos para maior precisão

2. **Principais alterações técnicas**:
   ```python
   # Antiga forma (Pydantic v1)
   @validator('data_validade')
   def data_validade_futuro(cls, v):
       # validação...
       return v
   
   # Nova forma (Pydantic v2)
   @field_validator('data_validade')
   def data_validade_futuro(cls, v: Optional[datetime]) -> Optional[datetime]:
       # validação...
       return v
   ```

3. **Alterações em configurações**:
   - Todas as classes usam `model_config = {"from_attributes": True}` em vez de `orm_mode = True`
   - Exemplos de JSON usam `json_schema_extra` em vez de `schema_extra`

## Boas Práticas para Evitar Problemas Semelhantes

1. **Compatibilidade com Pydantic v2**:
   - Use `field_validator` em vez de `validator`
   - Use `model_config` em vez de Config subclasse
   - Use `from_attributes=True` em vez de `orm_mode=True`
   - Use `pattern` em vez de `regex` para validação de strings
   - Adicione tipos de retorno explícitos para maior segurança

2. **Estrutura de Classes**:
   - Evite herança múltipla ou complexa entre modelos Pydantic
   - Ao substituir campos herdados, mantenha a mesma tipagem para evitar conflitos
   - Prefira composição sobre herança para modelos complexos

3. **Validação e Tipos**:
   - Use Field(...) para campos obrigatórios
   - Use tipagem explícita para melhor verificação estática
   - Forneça valores default_factory para coleções

## Exemplos Práticos

### Definição Correta de Esquemas

```python
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    preco: float = Field(..., gt=0)
    codigo: str = Field(..., pattern=r'^[A-Z0-9]{6}$')  # Use pattern, não regex
    
    # Use field_validator e tipagem explícita de retorno
    @field_validator('nome')
    def nome_capitalizado(cls, v: str) -> str:
        return v.capitalize()
        
    model_config = {
        "from_attributes": True  # Use from_attributes, não orm_mode
    }
```

### Configuração de Modelo

```python
# Forma antiga (Pydantic v1)
class Config:
    orm_mode = True
    schema_extra = {
        "example": {"nome": "Produto A", "preco": 100.0}
    }

# Forma nova (Pydantic v2)
model_config = {
    "from_attributes": True,
    "json_schema_extra": {
        "example": {"nome": "Produto A", "preco": 100.0}
    }
}
```

## Referências

- [Documentação do Pydantic v2](https://docs.pydantic.dev/latest/migration/)
- [Guia de migração do Pydantic v1 para v2](https://docs.pydantic.dev/latest/migration/)
- [Códigos de erro do Pydantic](https://errors.pydantic.dev/latest/)

## Data da Resolução
20 de maio de 2025