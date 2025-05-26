# 🔒 Configuração CORS para HUBB ONE Assist

Este documento especifica as regras CORS (Cross-Origin Resource Sharing) definitivas para a integração entre frontend e backend do HUBB ONE Assist. Siga estas instruções para garantir que todas as solicitações entre origens funcionem corretamente.

## 🌐 Cenário de Implantação

### URLs de Produção (Domínios Personalizados)
**Backend:** https://api.hubbassist.com
**Frontend:** https://app.hubbassist.com

### URLs Alternativas (Replit)
**Backend:** https://hubb-one-assist-back-hubb-one.replit.app
**Frontend (Produção):** https://hubb-one-assist-front-hubb-one.replit.app
**Frontend (Desenvolvimento):** Várias URLs do Replit (spock.replit.dev, worf.replit.dev, etc.)

## ⚙️ Configuração CORS no Backend (FastAPI)

O middleware CORS deve ser configurado no arquivo `app/main.py` conforme abaixo:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="HUBB ONE Assist API",
    description="Backend para o sistema HUBB ONE Assist",
    version="0.1.0",
)

# Lista definitiva de origens permitidas
# NUNCA use ["*"] com allow_credentials=True (violação de segurança)
allowed_origins = [
    # Ambientes de desenvolvimento local
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Create React App dev server
    
    # URLs de desenvolvimento do Replit (atualizar conforme necessário)
    "https://32c76b88-78ce-48ad-9c13-04975e5e14a3-00-12ynk9jfvcfqw.worf.replit.dev",
    "https://977761fe-66ad-4e57-b1d5-f3356eb27515-00-1yp0n9cqd8r5p.spock.replit.dev",
    "https://977761fe-66ad-4e57-b1d5-f3356eb27515-00-1yp0n9cqd8r5p.replit.dev",
    
    # URLs de produção
    "https://hubb-one-assist-v1-frontend-replit.replit.app",
    "https://hubb-one-assist-front-hubb-one.replit.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,  # ESSENCIAL para enviar cookies
    allow_methods=["*"],     # Permitir todos os métodos HTTP
    allow_headers=["*"],     # Permitir todos os cabeçalhos
    expose_headers=["*"]     # Expor todos os cabeçalhos
)
```

### ⚠️ Parâmetros Críticos

| Parâmetro | Valor | Importância |
|-----------|-------|-------------|
| `allow_credentials` | `True` | **CRÍTICO** - Permite envio de cookies entre origens. Sem isso, a autenticação JWT em cookies não funciona. |
| `allow_origins` | Lista específica | **CRÍTICO** - Define exatamente quais origens podem acessar a API. A especificação CORS não permite `["*"]` com credentials. |

## 🔧 Configuração no Frontend (React/Axios)

### Configuração do Cliente Axios

O arquivo de configuração do cliente Axios (`src/services/api.ts` ou similar) deve incluir:

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://hubb-one-assist-back-hubb-one.replit.app',
  withCredentials: true,  // CRÍTICO - Permite envio de cookies com solicitações
  headers: {
    'Content-Type': 'application/json',
  }
});

export default api;
```

### Para Requisições Fetch

Se usar Fetch API diretamente:

```javascript
fetch('https://hubb-one-assist-back-hubb-one.replit.app/auth/login', {
  method: 'POST',
  credentials: 'include',  // CRÍTICO - equivalente a withCredentials no Axios
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ email, password })
})
```

## 🔍 Verificação e Diagnóstico

### Como Verificar se o CORS está Funcionando

1. Abrir Console do Navegador (F12)
2. Ir para a aba "Network"
3. Procurar por solicitações à API
4. Verificar os cabeçalhos de resposta para:
   - `Access-Control-Allow-Origin: [sua origem]`
   - `Access-Control-Allow-Credentials: true`

### Erros Comuns e Soluções

| Erro | Causa | Solução |
|------|-------|---------|
| "Response to preflight request doesn't pass access control check" | Origem não permitida ou método OPTIONS não tratado | Adicionar a origem à lista `allow_origins` |
| "The value of the 'Access-Control-Allow-Origin' header must not be the wildcard '*' when the request's credentials mode is 'include'" | Usando `allow_origins=["*"]` com `allow_credentials=True` | Listar explicitamente todas as origens permitidas |
| "No 'Access-Control-Allow-Origin' header is present" | Middleware CORS não está ativo ou configurado | Verificar se o middleware está registrado antes de todos os routers |
| "Failed to fetch" com cookies | `withCredentials: false` ou sem `credentials: 'include'` | Configurar frontend para incluir credenciais |

## 🔄 Fluxo Correto de Solicitações CORS

1. Frontend faz solicitação para endpoint do backend
2. Navegador envia preflight OPTIONS para verificar permissões CORS
3. Backend responde com cabeçalhos CORS permitindo a origem
4. Navegador procede com a solicitação real (GET, POST, etc.)
5. Backend responde com dados e cabeçalhos CORS
6. Frontend processa a resposta

## 💻 Exemplos de Código Detalhados

### Login (Frontend)

```typescript
// Exemplo correto de login com Axios
async function login(email: string, password: string) {
  try {
    const response = await api.post('/auth/login', {
      email,
      password
    });
    
    // Cookies são enviados automaticamente com credentials:true
    return response.data;
  } catch (error) {
    console.error('Erro no login:', error);
    throw error;
  }
}
```

### Obter Lista de Assinantes (Frontend)

```typescript
// Exemplo correto de obter assinantes (rota protegida)
async function getSubscribers() {
  try {
    // IMPORTANTE: Usar a rota correta
    const response = await api.get('/subscribers/');
    
    // NÃO FAZER: Usar rotas inexistentes
    // const response = await api.get('/external-api/subscribers');
    
    return response.data;
  } catch (error) {
    console.error('Erro ao obter assinantes:', error);
    throw error;
  }
}
```

## ⚠️ Solução para Problemas Persistentes

Se os problemas CORS persistirem mesmo após seguir todas as configurações acima:

1. **Verifique os middlewares FastAPI:** a ordem importa; o CORS deve ser registrado antes dos routers
2. **Force a atualização dos cookies no navegador:** limpe o cache e cookies do site
3. **Verifique os logs do servidor:** procure erros relacionados à middleware CORS
4. **Adicione logs de depuração temporários:**

```python
@app.middleware("http")
async def log_cors_debug(request: Request, call_next):
    """Middleware temporário de depuração CORS"""
    print(f"Recebida requisição de: {request.headers.get('Origin', 'Unknown')}")
    print(f"Método: {request.method}")
    print(f"Caminho: {request.url.path}")
    
    response = await call_next(request)
    
    print("Cabeçalhos de resposta:")
    for name, value in response.headers.items():
        if name.startswith("access-control-"):
            print(f"  {name}: {value}")
    
    return response
```

## 📋 Checklist Final

- [ ] Backend tem CORS configurado com `allow_credentials=True`
- [ ] Todas as origens do frontend estão na lista `allow_origins`
- [ ] O domínio personalizado `https://app.hubbassist.com` está na lista de origens permitidas
- [ ] Frontend usa `withCredentials: true` ou `credentials: 'include'`
- [ ] Frontend usa as URLs corretas para a API (`https://api.hubbassist.com` ou URL alternativa)
- [ ] Ambos frontend e backend usam HTTPS
- [ ] Cookies no backend estão configurados com `SameSite="none", Secure=True`

## 📚 Recursos e Documentação

- [Documentação FastAPI sobre CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN: Cross-Origin Resource Sharing](https://developer.mozilla.org/pt-BR/docs/Web/HTTP/CORS)
- [Axios Docs - withCredentials](https://axios-http.com/docs/req_config)

## 📌 Última atualização

- Versão: `v1.0`
- Data: `2025-05-12`
- Responsável técnico: **Luis Paim**