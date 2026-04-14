# PLANO.md

## Visão Geral do Projeto

**Nome:** Mentions On-Demand (Sistema de Busca em Vídeos de TV)
**Versão:** 1.3.1
**Data de Atualização:** 2026-04-10

### Resumo
Sistema IA-powered para monitoramento personalizado de conteúdo televisivo. Utiliza as capacidades de **Program Grid** e **Transcription Façade** da Kantar para permitir que clientes monitorem termos específicos, marcas ou tópicos em grades de programação selecionadas, gerando relatórios detalhados e clips de vídeo.

### Diretrizes de UX/UI e Publicação
- **Prioridade Desktop:** Operação otimizada para desktop. Layout responsivo para celular como secundário.
- **Multilíngue:** Suporte nativo a PT, EN e ES.
- **Publicação:** Não publicar no here.now a partir de agora.

### Escopo
- [ ] Autenticação de usuários (Cliente, Operador e Administrador)
- [x] Integração com AgentMail para notificações
- [x] Interface de consulta à grade de programação externa
- [x] Gestão de Conjuntos de Monitoramento (MonitoringSets) e Regras (MonitoringRules)
- [x] Fluxo de aprovação comercial/crédito com justificativa de exceção
- [ ] Processamento de vídeos via **Transcription Façade (Kantar)**
- [x] Painel de ocorrências e geração de relatórios
- [ ] Integração de **Dados de Audiência** (Opcional/Premium)
- [ ] Geração de Clips de Vídeo com **Contexto** (Offset de segundos)
- [ ] CRUD de Configuração de Relatórios (Periodicidade, busca, download)
- [ ] Painel de Faturamento Mensal (Invoices)
- [x] Módulo do Operador (Aprovações, Gestão de Crédito, Bloqueio)
- [x] Dashboard de Saúde do Sistema (Monitoramento de Dispatcher/Engine)
- [ ] Log de Auditoria do Operador (Read-only para Admin)
- [ ] Integração com ERP (**Microsoft Dynamics AX**)

---

## Pendências Críticas
1. **Tabela de Preços:** Estratégia baseada em Minutos, Termos, Região e Impostos.
2. **Score de Crédito:** Definição da fonte/tabela de score para automação de aprovação.
3. **API de Audiência:** Regras de integração com o serviço de Realtime da Kantar Ibope Media.

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
1. **v1.2.1:** Implementação inicial do CRUD de Sets e Dashboard Streamlit.
2. **v1.3.0:** Refinamento total baseado no Roadmap Kantar (PPT): Inclusão de Audiência, Contexto de Vídeo, ERP Dynamics AX e Auditoria de Operador.
3. **v1.3.1:** 
    - Unificação da interface do cliente (Meus Conjuntos agora integra a criação de novos sets).
    - Implementação completa do Dashboard do Operador: Gestão de Clientes (Bloqueio/Crédito), Aprovações e Reprocessamento técnico.
    - Navegação robusta multilingue (PT/EN/ES) baseada em chaves internas.
    - Correção de fluxos de edição e exclusão de monitoramentos.
    - Integração do serviço de e-mail no dashboard.


---

## Configurações (.env)
```env
AGENTMAIL_API_KEY=am_us_...
DATABASE_URL=postgresql://mentions_app:app_secure_pass@localhost:5432/mentions_db
KANTAR_FACADE_API_KEY=...
ERP_AX_ENDPOINT=...
```
