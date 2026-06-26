# PLANO.md

## Visão Geral do Projeto

**Nome:** Mentions On-Demand (Sistema de Busca em Vídeos de TV)
**Versão:** 1.3.7
**Data de Atualização:** 2026-06-26

### Resumo
Sistema IA-powered para monitoramento personalizado de conteúdo televisivo. Utiliza as capacidades de **Program Grid** e **Transcription Façade** da Kantar para permitir que clientes monitorem termos específicos, marcas ou tópicos em grades de programação selecionadas, gerando relatórios detalhados e clips de vídeo.

### Diretrizes de UX/UI e Publicação
- **Prioridade Desktop:** Operação otimizada para desktop. Layout responsivo para celular como secundário.
- **Multilíngue:** Suporte nativo a PT, EN e ES.
- **Publicação:** NÃO publicar no here.now (somente webservice local).
- **Identidade Visual:** Alinhada ao padrão **AdInsights** (Kantar IBOPE Media).

### Escopo
- [x] Autenticação de usuários (Cliente, Operador e Administrador)
- [x] Integração com AgentMail para notificações
- [x] Interface de consulta à grade de programação externa
- [x] Gestão de Conjuntos de Monitoramento (MonitoringSets) e Regras (MonitoringRules)
- [x] Fluxo de aprovação comercial/crédito com justificativa de exceção
- [ ] Processamento de vídeos via **Transcription Façade (Kantar)**
- [x] Painel de ocorrências e geração de relatórios
- [x] Integração de **Dados de Audiência** (Opcional/Premium)
- [ ] Geração de Clips de Vídeo com **Contexto** (Offset de segundos)
- [ ] CRUD de Configuração de Relatórios (Periodicidade, busca, download)
- [ ] Painel de Faturamento Mensal (Invoices)
- [x] Módulo do Operador (Aprovações, Gestão de Crédito, Bloqueio, Cadastro Público)
- [x] Dashboard de Saúde do Sistema (Monitoramento de Dispatcher/Engine)
- [x] Gestão de Equipe Interna (Admin)
- [ ] Log de Auditoria do Operador (Read-only para Admin)
- [ ] Gestão completa de documentos (versão, substituição, histórico)
- [ ] Integração com ERP (**Microsoft Dynamics AX**)
- [ ] [CRÍTICO - DEV ONLY] Remover redirecionamento de e-mail para `eduardo.fonseca@ibope.com` no `EmailService` ao finalizar o projeto.

---

## Pendências Críticas
1. **[x] BUG - Upload de Documentos (RESOLVIDO):** O fluxo de submissão de múltiplos documentos (Silva MKT) foi completamente corrigido no frontend e backend com envios individuais e sequenciais resilientes em tela dedicada.
2. **Tabela de Preços:** Estratégia baseada em Minutos, Termos, Região e Impostos.
3. **Score de Crédito:** Definição da fonte/tabela de score para automação de aprovação.
4. **API de Audiência:** Regras de integração com o serviço de Realtime da Kantar Ibope Media.

---

## Decisões Técnicas

### Stack Tecnológica

| Componente | Tecnologia Escolhida | Status |
|------------|---------------------|--------|
| Frontend | `Streamlit (Protótipo) / React (Final)` | ✅/⏳ |
| Backend | `FastAPI (Python)` | ✅ |
| Banco de Dados | `PostgreSQL` | ✅ |
| Motor de Transcrição | `Transcription Façade (Kantar)` | ⏳ |
| Motor de Análise | `Content Analyzer (Mentions AI Engine)` | ⏳ |
| Reconhecimento de Imagem | `YoLo (Fase Futura)` | ⏳ |
| Infraestrutura | `Escalabilidade On-Demand (Cloud)` | ⏳ |

---

## Histórico de Implementação Recente
1. **v1.3.1:** Unificação de interface, Dashboard do Operador, Navegação Multilingue.
2. **v1.3.2:** Redirecionamento de e-mail (Dev), Dados de Audiência Premium, Simulação de Menções Enriquecida.
3. **v1.3.3:** Novo Onboarding Self-Service (Upload de documentos pelo cliente, status pending_approval inicial, bloqueio automático).
4. **v1.3.4:** Auto-aprovação de MonitoringSets, melhorias no Operador e correções de segurança.
5. **v1.3.5:** 
    - **Identidade Visual:** Aplicado padrão AdInsights (Kantar Blue #0F21FD, tipografia Geist/Verdana).
    - **Logotipo:** Restauração e centralização absoluta do logo oficial Kantar IBOPE Media.
    - **Idiomas:** Seletor híbrido estável com bandeiras circulares (HTML/SVG) e troca via URL.
    - **UX/UI:** Botões cinza corporativo, fontes maiores no sidebar e novo card de perfil de usuário.
    - **Fix:** Correção de KeyErrors no dicionário de tradução e centralização de textos no login.
6. **v1.3.6:**
    - **Onboarding e Uploads (Silva MKT):** Fluxo de submissão de documentos sequencial, resiliente e tela dedicada "Docs & Contratos".
    - **Módulos do Operador:** Dashboards completos de "Saúde", "Gestão de Clientes" (com aprovação em 1 clique, download de docs e limite de crédito) e "Aprovações Pendentes".
    - **Fix Idiomas e Sessão:** Chaveamento de idiomas 100% resiliente com chaves estáticas formatadas e persistência via UUID na URL.
    - **Separação de Páginas:** Divisão limpa em "Relatórios" (operacional) e "Faturamento & Faturas" (financeiro).
    - **Visualização de Ocorrências:** Painel de menções completo com grifo (highlighting) de tags, filtros por canal, métricas de audiência (Rating/Share), player de clipe em vídeo e botão simulador.
    - **Relatórios On-Demand:** Geração on-demand de relatórios em PDF no histórico do cliente com um clique.
7. **v1.3.7 (Atual):**
    - **Melhoria da Grade de Programação:** Redefinição de escopo para focar em 5 canais nacionais (Globo, SBT, Record, RedeTV e Bandeirantes) com dados de programação 100% reais e precisos entre 08:00 e 23:00 (todos os 7 dias, totalizando os 370 slots exatos das grades brasileiras).
    - **Novo Fluxo de UX/UI para Monitoramento:** Removido o fluxo antigo de busca genérica por texto. Agora o cliente inicia escolhendo o canal, depois o programa específico da grade, o que habilita um seletor interativo de dias da semana (preenchido de forma inteligente com os dias típicos de exibição do programa) permitindo habilitar/desabilitar dias antes de incluir.
    - **Exibição Inteligente na Home:** Os canais, programas e dias de monitoramento de cada conjunto agora são exibidos diretamente nos cards da tela principal para maior controle visual.
    - **Reestruturação Completa da Tela de Relatórios:**
        - **Painel de Atividade (KPIs):** Adicionados indicadores rápidos e analíticos mostrando as ocorrências totais, emissora líder e programa líder para o conjunto selecionado.
        - **Filtro de Data para Geração On-Demand:** Modificados o frontend e backend para suportar a seleção de um período customizado (Data de Início e Data de Fim) para gerar o relatório consolidado exato do intervalo desejado.
        - **Cards de Histórico Premium:** Tabela antiga em pandas cru foi substituída por um feed de cards modernos contendo o nome limpo do arquivo, datas formatadas de geração, período de cobertura amigável, indicador do output real de valor (quantidade de menções capturadas no período) e um botão de download estilizado no azul Kantar.

---

## Configurações (.env)
```env
AGENTMAIL_API_KEY=am_us_...
DATABASE_URL=postgresql://mentions_app:app_secure_pass@localhost:5432/mentions_db
KANTAR_FACADE_API_KEY=...
ERP_AX_ENDPOINT=...
```
