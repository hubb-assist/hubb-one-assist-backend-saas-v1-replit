# Relatório de Incidente: Perda Temporária de Rotas da API

## Data do Incidente
20 de maio de 2025

## Descrição do Problema
Durante a implementação do módulo de Insumos usando arquitetura DDD (Domain-Driven Design), ocorreu uma perda temporária das rotas da API originalmente implementadas. Após a implementação e deploy, foi observado que apenas os endpoints de Insumos e alguns endpoints padrão estavam disponíveis na documentação Swagger, enquanto todos os outros endpoints (autenticação, usuários, segmentos, módulos, planos, assinantes, pacientes, etc.) não estavam mais acessíveis.

## Causa Raiz
A causa raiz do problema foi identificada como a perda das referências aos routers originais no arquivo `app/main.py`. Durante a refatoração para adicionar o módulo de Insumos, apenas o router de insumos foi incluído no aplicativo FastAPI, resultando na perda de visibilidade e acesso a todos os outros endpoints.

Especificamente:
1. O arquivo principal `app/main.py` foi modificado para incluir apenas o router de insumos
2. As importações e inclusões dos routers originais foram removidas
3. Isso resultou na não exposição de todas as outras rotas da API na documentação Swagger e tornou os endpoints inacessíveis

## Impacto
O impacto deste incidente incluiu:
- Perda temporária de acesso a todas as funcionalidades da API, exceto Insumos
- Risco de interrupção dos serviços do frontend que dependem dessas APIs
- Potencial impacto em usuários finais da plataforma

## Ação Corretiva Tomada
1. Investigação imediata do problema ao observar a ausência de endpoints na documentação Swagger
2. Identificação da causa raiz (remoção de routers do arquivo main.py)
3. Localização de todos os arquivos de rotas originais presentes no sistema (`app/api/routes_*.py`)
4. Restauração de todas as importações e inclusões de routers no arquivo `app/main.py`
5. Reinício do servidor para aplicar as alterações
6. Verificação da documentação Swagger para confirmar a restauração de todos os endpoints

## Lições Aprendidas e Recomendações

### Para Desenvolvedores:
1. **NUNCA excluir ou substituir completamente importações existentes**: Ao adicionar novos módulos, sempre faça isso de forma incremental, mantendo as funcionalidades existentes.
2. **Revisão de código antes de commits**: Implementar revisões de código obrigatórias para garantir que alterações não removam funcionalidades existentes.
3. **Testes antes de deploy**: Executar testes completos antes de implantar para garantir que todas as rotas continuam funcionando.

### Práticas para Evitar Recorrência:
1. **Implementar versionamento adequado de código**: Garantir que o sistema de controle de versão (Git) esteja sendo usado corretamente para possibilitar rollbacks rápidos.
2. **Backup regular do código-fonte**: Manter backups regulares para recuperação rápida em caso de problemas.
3. **Documentação de endpoints essenciais**: Manter uma lista de todos os endpoints críticos que devem estar sempre disponíveis.
4. **Testes automatizados**: Desenvolver testes que verifiquem a disponibilidade de todas as rotas críticas.

### Mudanças de Processo Recomendadas:
1. **Ambientes de staging**: Implementar um ambiente de staging para testar alterações antes do deploy em produção.
2. **Checklist de deployment**: Criar uma checklist de verificação pré-deploy que inclua verificar se todas as rotas estão disponíveis.
3. **Monitoramento de endpoints**: Implementar monitoramento automático de endpoints críticos para alertar sobre indisponibilidades.

## Plano de Prevenção Futura
1. Desenvolver e manter um conjunto de testes automatizados para verificar a disponibilidade de todos os endpoints críticos
2. Implementar uma revisão de código mais rigorosa para mudanças em arquivos fundamentais como `main.py`
3. Adicionar monitoramento contínuo de endpoints para detectar rapidamente qualquer indisponibilidade
4. Implementar backup automático do código antes de modificações significativas
5. Configurar alertas de disponibilidade de API

## Conclusão
Este incidente, embora tenha causado uma interrupção temporária, foi rapidamente identificado e resolvido. As medidas preventivas recomendadas, se implementadas, reduzirão significativamente o risco de ocorrências semelhantes no futuro.

---

*Documento elaborado por: Equipe de Desenvolvimento HUBB ONE Assist*
*Data: 20 de maio de 2025*