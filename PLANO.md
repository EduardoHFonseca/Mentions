# PLANO.md

## Visão Geral do Projeto

**Nome:** Mentions On-Demand (Sistema de Busca em Vídeos de TV)
**Versão:** 1.4.4
**Data de Atualização:** 2026-07-22

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
- [x] Processamento assíncrono de vídeos via **Transcription Façade (Kantar)** (Fila FIFO da Madrugada)
- [x] Painel de ocorrências e geração de relatórios
- [x] Integração de **Dados de Audiência** (Opcional/Premium)
- [x] Geração e Recorte de Clips de Vídeo com **Contexto** (Offset de segundos) na fila de tarefas
- [x] Envio de Relatório Diário D+1 via **E-mail HTML** formatado (sem dependência vital de PDF)
- [x] Painel de Faturamento Mensal (Invoices) e Simulador PIX/Boleto
- [x] Módulo do Operador (Aprovações, Gestão de Crédito, Bloqueio, Cadastro Público)
- [x] Dashboard de Saúde do Sistema (Monitoramento de Dispatcher/Engine)
- [x] Gestão de Equipe Interna (Admin)
- [x] Log de Auditoria do Operador (Read-only para Admin)
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
7. **v1.3.7:**
    - **Melhoria da Grade de Programação:** Redefinição de escopo para focar em 5 canais nacionais (Globo, SBT, Record, RedeTV e Bandeirantes) com dados de programação 100% reais e precisos entre 08:00 e 23:00 (todos os 7 dias, totalizando os 370 slots exatos das grades brasileiras).
    - **Novo Fluxo de UX/UI para Monitoramento:** Removido o fluxo antigo de busca genérica por texto. Agora o cliente inicia escolhendo o canal, depois o programa específico da grade, o que habilita um seletor interativo de dias da semana (preenchido de forma inteligente com os dias típicos de exibição do programa) permitindo habilitar/desabilitar dias antes de incluir.
    - **Exibição Inteligente na Home:** Os canais, programas e dias de monitoramento de cada conjunto agora são exibidos diretamente nos cards da tela principal para maior controle visual.
    - **Reestruturação Completa da Tela de Relatórios:**
        - **Painel de Atividade (KPIs):** Adicionados indicadores rápidos e analíticos mostrando as ocorrências totais, emissora líder e programa líder para o conjunto selecionado.
        - **Filtro de Data para Geração On-Demand:** Modificados o frontend e backend para suportar a seleção de um período customizado (Data de Início e Data de Fim) para gerar o relatório consolidado exato do intervalo desejado.
        - **Cards de Histórico Premium:** Tabela antiga em pandas cru foi substituída por um feed de cards modernos contendo o nome limpo do arquivo, datas formatadas de geração, período de cobertura amigável, indicador do output real de valor (quantidade de menções capturadas no período) e um botão de download estilizado no azul Kantar.
8. **v1.3.8:**
    - **Fila de Tarefas Assíncronas (TaskQueue):** Implementação de fila FIFO persistente no PostgreSQL para gerenciar tarefas de transcrição e clipping em lote durante a madrugada.
    - **Transcription Façade & Video Clipping:** Processamento asíncrono que consome arquivos do repositório de vídeo, executa busca no Transcription Façade da Kantar e gera recortes de vídeo físicos (`clip_[id].mp4`) com margens de contexto configuráveis (offset).
    - **Relatório Automatizado D+1 por E-mail:** Geração automática e envio diário às 06h via e-mail HTML rico de todas as ocorrências mapeadas de D-1, detalhando ocorrências, time-stamps, dados de audiência premium e links seguros para reprodução instantânea no player do sistema.
    - **Scheduler Control (Operador):** Painel interativo de gerenciamento de tarefas no módulo do operador, permitindo visualizar a fila de processamento e executar manualmente (simulação da madrugada) a fila de forma assíncrona.
9. **v1.3.9:**
    - **Integração do Mercado Internacional (Holanda - NL):** Implementação de scraper e importador robusto (`src/scripts/import_nl_grid.py`) para capturar e granular a grade de programação nacional holandesa (NPO 1, NPO 2, NPO 3) diretamente de TVGids.nl.
    - **Enriquecimento de Metadados:** Mapeamento de status ao vivo, reprises, categorias (Esporte/Noticiário) e imagens oficiais (posters/thumbnails), armazenando-os de forma retrocompatível.
    - **Interface Visual Moderna (Streamlit):** Criação de seletor de País na interface e de cards ricos com pôsteres responsivos, badges coloridos corporativos e descrição formatada sob o padrão de design AdInsights.
    - **Correções de Compatibilidade:** Correção do aviso de depreciação do Streamlit de `use_column_width` para `use_container_width`.
10. **v1.4.0:**
    - **Monitoramento de Intervalos Comerciais (Anúncios & Breaks):** Implementação do seletor "Modo de Monitoramento" na tela de criação de conjuntos, permitindo alternar entre "Programas da Grade (Editorial)" e "Intervalos Comerciais (Anúncios & Breaks)".
    - **Cobertura Horária Customizável:** Suporte a monitoramento 24 horas (dia todo) e faixas horárias customizadas com seletores de Hora Início e Hora Fim (`st.time_input`), permitindo buscar anúncios em praças e emissoras específicas a qualquer hora.
    - **Internacionalização Híbrida:** Rótulos e mensagens totalmente traduzidos em PT, EN e ES.
11. **v1.4.1:**
    - **Painel de Faturamento Mensal Inteligente:** Reestruturação da tela "Faturamento & Faturas" com KPIs de limite de crédito em tempo real, cálculo de consumo estimado no ciclo D+0 baseado nos minutos e audiência premium, e extrato analítico de consumo.
    - **Pagamento Instantâneo PIX & Boletos:** Cards de faturas emitidas com chave PIX Copia e Cola, simulação de quitação instantânea no backend (`/api/invoices/{id}/pay`) e download de recibos/boletos em PDF.
    - **Validação Gradual de Documentos:** Implementação de regras de documentação em 4 níveis (`Sem Documentos`, `Envio Parcial`, `Pendente de Análise`, `Verificado`) no backend e frontend.
12. **v1.4.2:**
    - **Gestão de Perfil do Cliente:** Reformulação completa da tela "Meu Perfil", separando dados jurídicos protegidos (Razão Social, CNPJ e E-mail de login com trava de leitura) dos dados operacionais editáveis (Nome do Contato Principal, Telefone/WhatsApp e Endereço de Cobrança).
    - **Endpoint Seguro de Perfil:** Novo endpoint `PATCH /api/user/{user_id}/profile` permitindo alteração segura de dados de contato do cliente com atualização em tempo real na sessão do sistema.
13. **v1.4.3:**
    - **Módulo Administrador & Log de Auditoria:** Implementação das 3 abas no perfil Admin: (1) Feed de Auditoria dos Operadores (`GET /api/admin/logs`) com filtros por ação e justificativas, (2) Gestão de Equipe Interna com criação de novos usuários (`POST /api/admin/user`), (3) Parâmetros Globais do Sistema.
    - **Visualização de Documentos pelo Operador:** Adicionado link/botão para download e visualização direta dos arquivos anexos (`GET /api/user/document/{user_id}/{filename}`) na tela de gestão de clientes do Operador.
    - **Registro de Log Automático:** Registro transparente na tabela `operator_logs` para aprovações, ajustes de crédito e bloqueios/desbloqueios.
14. **v1.4.4 (Atual):**
    - **Persistência das Configurações Globais:** Implementação das rotas `GET /api/admin/config` e `POST /api/admin/config` no backend com persistência na tabela `system_configs` do PostgreSQL.
    - **Leitura & Gravação Dinâmica (Admin):** Conectado o formulário da aba "Configurações Globais" para ler os parâmetros salvos no banco de dados e aplicar atualizações em tempo real com feedback via Toast e reload automático da interface.

---

## Configurações (.env)
```env
AGENTMAIL_API_KEY=am_us_...
DATABASE_URL=postgresql://mentions_app:app_secure_pass@localhost:5432/mentions_db
KANTAR_FACADE_API_KEY=...
ERP_AX_ENDPOINT=...
```
