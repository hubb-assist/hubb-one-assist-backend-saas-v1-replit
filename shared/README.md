# Shared Types & Utilities

Esta pasta contém tipos TypeScript gerados automaticamente a partir da API OpenAPI e utilitários compartilhados.

## Como funciona

1. **Geração Automática**: O script lê `/openapi.json` da API
2. **Tipos Seguros**: Cria interfaces TypeScript para todos os modelos
3. **Cliente HTTP**: Gera funções prontas para chamar cada endpoint

## Exemplo do que será gerado

```typescript
// Tipos automáticos baseados na sua API FastAPI
export interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

export interface Patient {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  birth_date?: string;
}

// Cliente HTTP automático
export class UsersService {
  public static getUsers(): Promise<User[]> {
    // código gerado automaticamente
  }
  
  public static createUser(user: CreateUserRequest): Promise<User> {
    // código gerado automaticamente  
  }
}
```

## Comandos

```bash
# Gerar tipos (servidor local)
npm run generate:types

# Gerar tipos (produção)  
npm run generate:types:prod
```

Resultado: Frontend e backend sempre sincronizados, zero erros de tipo!