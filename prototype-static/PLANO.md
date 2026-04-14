# PLANO.md

## Visão Geral do Projeto

**Nome:** Mentions On-Demand (Sistema de Busca em Vídeos de TV)
**Versão:** 1.3.0
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
- [ ] Fluxo de aprovação comercial/crédito com justificativa de exceção
- [ ] Processamento de vídeos via **Transcription Façade (Kantar)**
- [x] Painel de ocorrências e geração de relatórios
- [ ] Integração de **Dados de Audiência** (Opcional/Premium)
- [ ] Geração de Clips de Vídeo com **Contexto** (Offset de segundos)
- [ ] CRUD de Configuração de Relatórios (Periodicidade, busca, download)
- [ ] Painel de Faturamento Mensal (Invoices)
- [ ] Módulo do Operador (Aprovações, Gestão de Crédito, Bloqueio)
- [ ] Dashboard de Saúde do Sistema (Monitoramento de Dispatcher/Engine)
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
| Frontend | `React/Next.js` | ⏳ |
| Backend | `FastAPI (Python)` | ✅ |
| Banco de Dados | `PostgreSQL` | ✅ |
| Motor de Transcrição | `Transcription Façade (Kantar)` | ⏳ |
| Motor de Análise | `Content Analyzer (Mentions AI Engine)` | ⏳ |
| Reconhecimento de Imagem | `YoLo (Fase Futura)` | ⏳ |
| Infraestrutura | `Escalabilidade On-Demand (Cloud)` | ⏳ |

---

## Modelos de Dados (Refinados)

### User (Usuário)
- **id**: UUID
- **email**: String (Unique)
- **company_name**: String
- **credit_limit**: Decimal
- **is_blocked_access**: Boolean (Bloqueio por inadimplência)
- **role**: Enum (`admin`, `client`, `operator`)

### MonitoringSet
- **id**: UUID
- **total_minutes_estimate**: Integer (Esforço de processamento)
- **status**: Enum (`stand_by`, `awaiting_approval`, `approved`, `active`)
- **audience_data_enabled**: Boolean

### OperatorLog (Auditoria)
- **id**: UUID
- **operator_id**: UUID
- **action**: String
- **justification**: String (Exigido para extrapolação de limite)

---

## Fluxos do Sistema

### Fluxo 1: Configuração e Aprovação
1. **Cliente** seleciona Canal/Programa na **Program Grid**.
2. O sistema calcula o **Volume de Processamento** (Esforço).
3. **Operador** valida o crédito:
    - Se ok: Aprova.
    - Se excedido: Exige justificativa (Aprovado por X).
4. Status ativação dispara ativação no **Scheduler/Dispatcher**.

### Fluxo 2: Execução e Notificação
1. **Dispatcher** localiza arquivos no **Capture DB**.
2. **Transcription Façade** converte áudio em texto.
3. **Content Analyzer** busca termos e registra timestamps.
4. **Report Generator** extrai clips (com offset de contexto) e anexa dados de audiência (se contratado).
5. Notificação via AgentMail.

### Fluxo 3: Faturamento (ERP)
1. Sistema envia dados de uso mensal para o **Microsoft Dynamics AX**.
2. ERP gera a fatura (Invoice) e o sistema disponibiliza o PDF no portal.

---

## Histórico de Implementação Recente
1. **v1.2.1:** Implementação inicial do CRUD de Sets e Dashboard Streamlit.
2. **v1.3.0:** Refinamento total baseado no Roadmap Kantar (PPT): Inclusão de Audiência, Contexto de Vídeo, ERP Dynamics AX e Auditoria de Operador.
