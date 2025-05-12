# 🛠️ Guia de Solução de Problemas CORS

Este documento apresenta um guia passo a passo para diagnosticar e resolver problemas de CORS (Cross-Origin Resource Sharing) no sistema HUBB ONE Assist.

## 📋 Checklist de Verificação Rápida

Quando encontrar erros de CORS, verifique imediatamente:

- [ ] O frontend está usando `credentials: 'include'` ou `withCredentials: true`?
- [ ] A URL do backend está correta (sem `/external-api/` ou outros prefixos incorretos)?
- [ ] A origem do frontend está na lista `allow_origins` do backend?
- [ ] O endpoint existe e está acessível de outras formas (via curl ou Postman)?
- [ ] Ambos frontend e backend estão usando HTTPS ou ambos HTTP (não misturados)?

## 🔍 Diagnóstico por Tipo de Erro

### 1. Erro: "No 'Access-Control-Allow-Origin' header is present on the requested resource"

**Causas possíveis:**
- Origem não incluída na lista `allow_origins`
- Middleware CORS não está registrado corretamente
- Erro 500 no servidor antes que o middleware CORS possa responder

**Soluções:**
1. Adicione a origem exata do frontend à lista `allow_origins`
2. Verifique se o middleware CORS está registrado antes dos routers
3. Verifique os logs do servidor para erros 500

### 2. Erro: "The value of the 'Access-Control-Allow-Origin' header must not be the wildcard '*' when the request's credentials mode is 'include'"

**Causas possíveis:**
- Usando `allow_origins=["*"]` junto com `allow_credentials=True`

**Soluções:**
1. Liste explicitamente todas as origens permitidas em vez de usar `["*"]`

### 3. Erro: "Failed to fetch" ou "Network Error" com CORS

**Causas possíveis:**
- Cookies de autenticação expirados ou inválidos
- Erro de rede não relacionado ao CORS
- URL do backend incorreta

**Soluções:**
1. Faça logout e login novamente para renovar cookies
2. Verifique a URL do backend
3. Verifique a conexão de rede

### 4. Erro: Requisição OPTIONS rejeitada com 405 Method Not Allowed

**Causas possíveis:**
- Middleware CORS não está processando requisições OPTIONS corretamente

**Soluções:**
1. Certifique-se de que o middleware CORS está configurado antes de todos os routers

## 🔧 Ativando o Middleware de Depuração CORS

Para identificar problemas específicos, você pode ativar temporariamente o middleware de depuração CORS:

1. Edite `app/main.py`
2. Adicione:
   ```python
   from app.core.cors_debug import cors_debug_middleware
   
   # Adicionar após o middleware CORS padrão
   app.add_middleware(cors_debug_middleware)
   ```
3. Reinicie o backend
4. Execute a operação que está causando problemas
5. Verifique os logs para mensagens de diagnóstico detalhadas
6. **Importante:** Remova este middleware antes de implantar em produção!

## 🛠️ Ferramentas de Diagnóstico

### Console do Navegador

Use a aba Network (F12) para verificar:
1. Status das requisições OPTIONS (devem ser 200)
2. Cabeçalhos de resposta para verificar cabeçalhos CORS:
   - `Access-Control-Allow-Origin`
   - `Access-Control-Allow-Credentials`
   - `Access-Control-Allow-Methods`
   
### cURL para testar backend diretamente

```bash
# Testar preflight OPTIONS
curl -v -X OPTIONS -H "Origin: https://your-frontend-origin.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     https://your-backend-url.com/endpoint

# Testar GET com credenciais
curl -v -X GET -H "Origin: https://your-frontend-origin.com" \
     --cookie "token=your-jwt-token" \
     https://your-backend-url.com/endpoint
```

## 🧰 Soluções Comuns por Componente

### Backend (FastAPI)

```python
# 1. Verifique a configuração CORS em app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Adicione todas as suas origens aqui
        "https://sua-origem-frontend.com",
    ],
    allow_credentials=True,  # Deve ser True para cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Verifique a configuração de cookies em todos os endpoints de autenticação
@app.post("/auth/login")
async def login(response: Response):
    # ...
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=True,  # True para HTTPS
        samesite="none",  # Importante para CORS
        max_age=1800,
    )
```

### Frontend (React/Axios)

```typescript
// 1. Configuração correta do Axios
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://your-backend-url.com',
  withCredentials: true,  // CRÍTICO para cookies
});

// 2. Uso correto para chamadas específicas
async function login(email, password) {
  try {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  } catch (error) {
    console.error('Erro:', error);
    throw error;
  }
}
```

## 📚 Padrões de Requisição e Respostas CORS

### Preflight OPTIONS

**Requisição:**
```
OPTIONS /endpoint HTTP/1.1
Host: your-backend-url.com
Origin: https://your-frontend-origin.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type
```

**Resposta correta:**
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://your-frontend-origin.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Credentials: true
```

### Requisição real com cookies

**Requisição:**
```
GET /endpoint HTTP/1.1
Host: your-backend-url.com
Origin: https://your-frontend-origin.com
Cookie: token=your-jwt-token
```

**Resposta correta:**
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://your-frontend-origin.com
Access-Control-Allow-Credentials: true
Content-Type: application/json

{"data": "your data here"}
```

## 📌 Última atualização

- Versão: `v1.0`
- Data: `2025-05-12`
- Responsável técnico: **Luis Paim**