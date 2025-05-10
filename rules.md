# 📐 HUBB Assist — Regras Oficiais do Projeto (Replit + FastAPI)

Este arquivo define as **regras obrigatórias** para o desenvolvimento do backend do projeto **HUBB ONE Assist** dentro do ambiente Replit.  
Todas as ações executadas pelo Replit AI ou por colaboradores devem seguir fielmente estas diretrizes.

---

## 🚫 Regras de Proibição (NUNCA fazer)

- ❌ **Nunca usar Flask, Flash ou qualquer servidor WSGI**  
  > Este projeto utiliza exclusivamente o framework **FastAPI**, que é baseado em ASGI.  
  > *Por favor, não tente usar Flask como proxy, servidor ou intermediário.*

- ❌ **Não utilizar Gunicorn diretamente**  
  > O servidor padrão é **Uvicorn**. Gunicorn só deve ser usado com workers ASGI avançados (não se aplica aqui).

- ❌ **Não criar arquivos como `run_fastapi.py`, `app.py`, `main_flask.py`**  
  > O ponto de entrada único da aplicação deve ser `main.py`, dentro da estrutura do projeto.

- ❌ **Não sobrescrever o Swagger UI (/docs)**  
  > A página `/` pode exibir uma mensagem HTML informativa, mas **jamais deve redirecionar ou bloquear o acesso ao `/docs`**.

---

## ✅ Padrões obrigatórios

- ✅ **Framework principal:** `FastAPI`
- ✅ **Servidor:** `Uvicorn`
- ✅ **Banco de Dados:** `PostgreSQL` via `SQLAlchemy`
- ✅ **ORM:** `SQLAlchemy 2.0` + Alembic
- ✅ **Validações:** `Pydantic v2`
- ✅ **Autenticação:** JWT com Cookies HttpOnly (em módulos futuros)
- ✅ **Hash de senha:** `bcrypt`
- ✅ **Env vars:** Lidas via `python-dotenv`
- ✅ **Repositório organizado por camadas:**  
  - `app/api/` — rotas  
  - `app/services/` — lógica de negócio  
  - `app/db/` — modelos, sessão, migrations  
  - `app/schemas/` — validações com Pydantic

---

## 📁 Estrutura mínima de diretórios

```
app/
├── api/
├── db/
├── services/
├── schemas/
├── main.py
├── init.py
```

---

## 🌍 Localização e idioma

- Todos os comentários, mensagens de log e respostas da API devem estar em **português**.
- A documentação da API (`/docs`) deve estar legível em português para facilitar uso clínico e comercial.

---

## 🧪 Boas práticas adicionais

- ✅ Utilizar nomes de variáveis claros e autoexplicativos (ex: `usuario`, `email`, `senha_hashed`)
- ✅ Usar UUID como chave primária para usuários e recursos principais
- ✅ Rotas sempre com prefixo `/api/v1/` e organizadas por domínio
- ✅ Não duplicar lógica entre service e controller
- ✅ Comentários devem ser objetivos e somente quando o código não for autoexplicativo

---

## 🔐 Segurança

- ✅ JWT com HttpOnly cookies
- ✅ Proteção de rotas com roles/papéis (`SUPER_ADMIN`, `DIRETOR`, `COLABORADOR`)
- ✅ Logs sensíveis devem ser filtrados (nunca logar senhas ou tokens)

---

## 🧠 Inteligência Artificial (Replit AI Agent)

- 📌 Ao utilizar o Replit AI, **instruções devem ser dadas sempre com clareza no início do prompt**.
- Sempre reforce:  
  > "**Não use Flask. Use apenas FastAPI com Uvicorn.**"

---

## 🔒 Regras de Controle de Escopo e Execução

### 🚫 Não realizar ações proativas não solicitadas

- A IA não deve criar arquivos, funções ou estruturas adicionais além do que foi claramente especificado na tarefa.
- Se algo for necessário para o funcionamento, a IA deve perguntar ou comentar antes de executar.

### 🚫 Não criar páginas HTML, interfaces, layouts ou endpoints extras sem solicitação explícita

- Ex: "Aproveitei para criar uma página informativa" ou "adicionei um recurso extra" é terminantemente proibido.

### 🚫 Não modificar arquivos existentes sem orientação expressa

- Atualizações em main.py, .replit, requirements.txt, schemas, etc., devem ser feitas apenas se forem necessárias para cumprir a tarefa atual e mencionadas claramente no prompt.

### 🚫 Não aplicar refatorações, renomeações ou reestruturações automáticas

- A IA não deve mover, renomear ou reagrupar arquivos com base em preferências próprias. A estrutura deve seguir exatamente o padrão definido anteriormente.

### 🚫 Não mudar comportamento de rotas, lógica ou responses sem ser solicitado

- A lógica de negócio e os retornos JSON devem permanecer conforme definido. Nenhuma alteração de resposta ou comportamento deve ser feita com base em suposição.

### 📋 Procedimentos obrigatórios antes de agir

- ✅ Se uma tarefa depender de arquivos ou dados ainda não criados, solicite autorização antes de criar.
- ✅ Caso uma tarefa pareça incompleta ou ambígua, a IA deve pedir esclarecimento antes de prosseguir.
- ✅ Toda ação da IA deve ser precedida de explicação clara do que será feito e por quê — especialmente se envolver alterações em arquivos compartilhados.

### 📌 Regra geral para uso do Replit AI Agent

- O Replit AI só pode executar o que for explicitamente descrito na tarefa ou o que for tecnicamente necessário para concluir a tarefa de forma funcional.
- Iniciativas extras, suposições ou "ajustes convenientes" são terminantemente proibidos.

---

## ⚠️ Regras contra soluções paliativas, simplificações ou "atalhos técnicos"

### 🚫 Não implementar soluções paliativas, temporárias ou "funciona por agora"

- Toda implementação deve ser pensada como definitiva, sustentável, e pronta para produção.
- Não use artifícios como: copiar JSON para simular banco, variáveis globais como cache, ou ignorações de validação.

### 🚫 Não simplificar a arquitetura para "resolver mais rápido"

- A IA não deve "simplificar" estruturas, como remover camadas (services, schemas, etc.), eliminar validações ou ignorar separação de responsabilidades.
- A arquitetura deve sempre seguir Clean Code, DDD e SOLID.

### 🚫 Não alterar estratégias técnicas decididas previamente

Por exemplo:
- Não mudar de PostgreSQL para SQLite
- Não substituir bcrypt por hashlib
- Não trocar pydantic por dataclasses
- Não converter UUID para string por conveniência

### 🚫 Não "comentar código para funcionar" ou desabilitar partes que dão erro

- Se houver erro, diagnostique e resolva da forma correta.
- Nunca comente trechos críticos, ignore exceções silenciosamente ou desative regras de validação.

### ✅ Regra de conduta técnica

- Toda solução entregue deve ser sólida, escalável, profissional e tecnicamente correta.
- Nada de gambiarras, simplificações, ajustes improvisados ou atalhos para "funcionar rapidinho".

### 🧠 Exemplo do que não é permitido:

- "Desativei a verificação de CORS por enquanto" ❌
- "Ignorei a validação do email para facilitar" ❌
- "Troquei o UUID por string porque estava dando erro" ❌
- "Usei uma lista em memória como banco temporário" ❌
- "Comentei a autenticação para o endpoint funcionar" ❌

---

## 📌 Última atualização

- Versão: `v1.1`
- Data: `2025-05-10`
- Responsável técnico: **Luis Paim**