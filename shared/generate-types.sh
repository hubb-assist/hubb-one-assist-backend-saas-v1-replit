#!/bin/bash

echo "🚀 Gerando tipos TypeScript a partir da API OpenAPI..."

# Verificar se o servidor está rodando
if curl -s http://localhost:5000/openapi.json > /dev/null; then
    echo "✅ Servidor local detectado - usando http://localhost:5000"
    npm run generate:types
else
    echo "🌐 Usando servidor de produção"
    npm run generate:types:prod
fi

echo "✅ Tipos TypeScript gerados com sucesso!"
echo "📁 Verifique a pasta ./generated para os arquivos gerados"