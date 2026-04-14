import streamlit as st
import pandas as pd
import uuid
import requests
import os
import sys
from datetime import time, datetime

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.services.email_service import email_service

API_BASE_URL = "http://localhost:8000/api"

# --- I18N DICTIONARY ---
LANG_DATA = {
    "GB": {
        "title": "Mentions On-Demand",
        "nav_new": "Schedule",
        "nav_list": "Monitoring",
        "nav_reports": "Reports & Billing",
        "nav_test": "Test Email",
        "header_new": "New Monitoring Set",
        "header_list": "My Monitoring Sets",
        "header_reports": "Reports, Downloads & Billing",
        "header_billing": "Billing History",
        "label_frequency": "Report Frequency",
        "label_hour": "Preferred Hour",
        "label_recipients": "Email Recipients (comma separated)",
        "btn_save_config": "Save Config",
        "th_date": "Generation Date",
        "th_period": "Period",
        "th_amount": "Amount",
        "th_due": "Due Date",
        "th_status": "Status",
        "header_test": "Email Test (AgentMail)",
        "label_name": "Monitoring Name",
        "label_terms": "Search Terms (Tags)",
        "label_channel": "Select Channel",
        "label_program": "Search TV Grid",
        "btn_add_term": "+ Add Term",
        "btn_add_rule": "Consult TV Grid",
        "btn_save_draft": "Save Draft",
        "btn_submit": "Send for Approval",
        "btn_load_mentions": "Load Mentions",
        "btn_sim_mention": "Simulate Mention",
        "status_stand_by": "STAND-BY",
        "status_awaiting": "AWAITING APPROVAL",
        "status_approved": "APPROVED",
        "status_active": "ACTIVE",
        "msg_saved": "Set saved successfully!",
        "msg_deleted": "Set deleted successfully!",
        "msg_no_sets": "No monitoring sets found.",
        "msg_no_mentions": "No mentions found for this set.",
        "msg_connection_error": "Connection error:",
        "th_channel": "Channel",
        "th_program": "Program",
        "th_time": "Time Window",
        "th_days": "Days",
        "th_actions": "Actions",
        "freq_daily": "Daily",
        "freq_weekly": "Weekly",
        "freq_monthly": "Monthly",
        "btn_edit_config": "Edit Configuration",
        "btn_cancel": "Cancel",
        "tab_occurrences": "Occurrences",
        "btn_logout": "Logout",
        "btn_new_set": "+ New Monitoring Set",
        "btn_back": "Back to List",
        "op_nav_approvals": "Pending Approvals",
        "op_nav_health": "System Health",
        "op_nav_clients": "Customer Management",
        "lbl_active_sets": "Active Sets",
        "lbl_total_min": "Total Min/Week",
        "btn_reprocess": "Reprocess",
        "btn_block": "Block",
        "btn_unblock": "Unblock",
        "btn_adjust_credit": "Adjust Credit"
    },
    "PT": {
        "title": "Mentions On-Demand",
        "nav_new": "Novo Agendamento",
        "nav_list": "Meus Conjuntos",
        "nav_reports": "Relatórios e Faturamento",
        "nav_test": "Teste de Email",
        "header_new": "Novo Conjunto de Monitoramento",
        "header_list": "Meus Conjuntos de Monitoramento",
        "header_reports": "Relatórios, Downloads e Faturas",
        "header_billing": "Histórico de Faturamento",
        "label_frequency": "Frequência do Relatório",
        "label_hour": "Horário Preferencial",
        "label_recipients": "Destinatários (separados por vírgula)",
        "btn_save_config": "Salvar Configuração",
        "th_date": "Data de Geração",
        "th_period": "Período",
        "th_amount": "Valor",
        "th_due": "Vencimento",
        "th_status": "Status",
        "header_test": "Teste de Envio (AgentMail)",
        "label_name": "Nome do Monitoramento",
        "label_terms": "Termos de Busca (Tags)",
        "label_channel": "Selecione o Canal",
        "label_program": "Buscar Programa na Grade",
        "btn_add_term": "+ Adicionar Termo",
        "btn_add_rule": "Consultar Grade de Programação",
        "btn_save_draft": "Salvar Rascunho",
        "btn_submit": "Enviar para Aprovação",
        "btn_load_mentions": "Carregar Ocorrências",
        "btn_sim_mention": "Simular Ocorrência",
        "status_stand_by": "STAND-BY",
        "status_awaiting": "AGUARDANDO APROVAÇÃO",
        "status_approved": "APROVADO",
        "status_active": "ATIVO",
        "msg_saved": "Conjunto salvo com sucesso!",
        "msg_deleted": "Conjunto excluído com sucesso!",
        "msg_no_sets": "Não há monitoramento cadastrado.",
        "msg_no_mentions": "Nenhuma ocorrência encontrada para este conjunto.",
        "msg_connection_error": "Erro de conexão:",
        "th_channel": "Canal",
        "th_program": "Programa",
        "th_time": "Horário",
        "th_days": "Dias",
        "th_actions": "Ações",
        "freq_daily": "Diário",
        "freq_weekly": "Semanal",
        "freq_monthly": "Mensal",
        "btn_edit_config": "Alterar Configuração",
        "btn_cancel": "Cancelar",
        "tab_occurrences": "Ocorrências",
        "btn_logout": "Encerrar Sessão",
        "btn_new_set": "+ Novo Conjunto",
        "btn_back": "Voltar para Lista",
        "op_nav_approvals": "Aprovações Pendentes",
        "op_nav_health": "Saúde do Sistema",
        "op_nav_clients": "Gestão de Clientes",
        "lbl_active_sets": "Sets Ativos",
        "lbl_total_min": "Total Min/Semana",
        "btn_reprocess": "Reprocessar",
        "btn_block": "Bloquear",
        "btn_unblock": "Desbloquear",
        "btn_adjust_credit": "Ajustar Crédito"
    },
    "ES": {
        "title": "Mentions On-Demand",
        "nav_new": "Nueva Agenda",
        "nav_list": "Mis Conjuntos",
        "nav_reports": "Informes y Facturación",
        "nav_test": "Prueba de Email",
        "header_new": "Nuevo Conjunto de Monitoreo",
        "header_list": "Mis Conjuntos de Monitoreo",
        "header_reports": "Informes, Descargas y Facturas",
        "header_billing": "Historial de Facturación",
        "label_frequency": "Frecuencia del Informe",
        "label_hour": "Hora Preferida",
        "label_recipients": "Destinatarios (separados por coma)",
        "btn_save_config": "Guardar Configuración",
        "th_date": "Fecha de Generación",
        "th_period": "Período",
        "th_amount": "Monto",
        "th_due": "Vencimiento",
        "th_status": "Estado",
        "header_test": "Prueba de Envío (AgentMail)",
        "label_name": "Nombre del Monitoreo",
        "label_terms": "Términos de Búsqueda",
        "label_channel": "Seleccione el Canal",
        "label_program": "Buscar Programa en la Parrilla",
        "btn_add_term": "+ Añadir Término",
        "btn_add_rule": "Consultar Parrilla de TV",
        "btn_save_draft": "Guardar Borrador",
        "btn_submit": "Enviar para Aprobación",
        "btn_load_mentions": "Cargar Ocurrencias",
        "btn_sim_mention": "Simular Ocurrencia",
        "status_stand_by": "STAND-BY",
        "status_awaiting": "ESPERANDO APROBACIÓN",
        "status_approved": "APROBADO",
        "status_active": "ACTIVO",
        "msg_saved": "¡Conjunto guardado con éxito!",
        "msg_deleted": "¡Conjunto eliminado con éxito!",
        "msg_no_sets": "No hay monitoreo registrado.",
        "msg_no_mentions": "No se encontraron ocurrencias para este conjunto.",
        "msg_connection_error": "Error de conexão:",
        "th_channel": "Canal",
        "th_program": "Programa",
        "th_time": "Ventana Horaria",
        "th_days": "Días",
        "th_actions": "Acciones",
        "freq_daily": "Diario",
        "freq_weekly": "Semanal",
        "freq_monthly": "Mensual",
        "btn_edit_config": "Cambiar Configuración",
        "btn_cancel": "Cancelar",
        "tab_occurrences": "Ocurrencias",
        "btn_logout": "Cerrar Sesión",
        "btn_new_set": "+ Nuevo Conjunto",
        "btn_back": "Volver a la Lista",
        "op_nav_approvals": "Aprobaciones Pendientes",
        "op_nav_health": "Salud del Sistema",
        "op_nav_clients": "Gestión de Clientes",
        "lbl_active_sets": "Sets Activos",
        "lbl_total_min": "Total Min/Semana",
        "btn_reprocess": "Reprocesar",
        "btn_block": "Bloquear",
        "btn_unblock": "Desbloquear",
        "btn_adjust_credit": "Ajustar Crédito"
    }
}

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
if 'lang' not in st.session_state: st.session_state.lang = "PT"
if 'edit_id' not in st.session_state: st.session_state.edit_id = None
if 'temp_terms' not in st.session_state: st.session_state.temp_terms = []
if 'temp_rules' not in st.session_state: st.session_state.temp_rules = []
if 'set_name' not in st.session_state: st.session_state.set_name = ""
if 'report_edit_mode' not in st.session_state: st.session_state.report_edit_mode = False
if 'show_form' not in st.session_state: st.session_state.show_form = False

L = LANG_DATA[st.session_state.lang]

# --- SHARED FUNCTIONS ---
def render_monitoring_form():
    st.header(L['header_new'] if not st.session_state.edit_id else f"{L['header_new']} (Editing)")
    
    if st.button(L['btn_back']):
        st.session_state.show_form = False
        st.session_state.edit_id = None
        st.session_state.set_name = ""
        st.session_state.temp_terms = []
        st.session_state.temp_rules = []
        st.rerun()

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            set_name = st.text_input(L['label_name'], value=st.session_state.set_name, placeholder="Ex: Safra 2026 - Soja")
            st.session_state.set_name = set_name
            
            st.write("---")
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                # Need to persist audience_enabled in session state for editing
                if 'audience_enabled' not in st.session_state: st.session_state.audience_enabled = False
                audience_enabled = st.checkbox("Incluir Dados de Audiência (Premium)", value=st.session_state.audience_enabled)
                st.session_state.audience_enabled = audience_enabled
            with col_opt2:
                if 'context_secs' not in st.session_state: st.session_state.context_secs = 15
                context_secs = st.number_input("Segundos de Contexto (Clip)", 5, 60, st.session_state.context_secs)
                st.session_state.context_secs = context_secs
        with col2:
            if 'term_input' not in st.session_state: st.session_state.term_input = ""
            
            def add_term():
                term = st.session_state.term_input
                if term and term not in st.session_state.temp_terms:
                    st.session_state.temp_terms.append(term)
                    st.session_state.term_input = "" # Clear input

            st.text_input(L['label_terms'], key="term_input", placeholder="Digite e clique em +", on_change=add_term)
            if st.button(L['btn_add_term']):
                add_term()
                st.rerun()
            
            if st.session_state.temp_terms:
                st.write("Tags:", " ".join([f"`{t}`" for t in st.session_state.temp_terms]))

    st.subheader(L['btn_add_rule'])
    
    # 1. Channel Selection
    channels = []
    try:
        channels_res = requests.get(f"{API_BASE_URL}/grid/channels")
        if channels_res.status_code == 200:
            channels = sorted(channels_res.json())
    except:
        st.error("Erro ao carregar canais.")

    selected_channel = st.selectbox(L['label_channel'], options=[""] + channels)

    # 2. Program Search (Filtered by Channel)
    search_q = st.text_input(L['label_program'], placeholder="Digite o nome do programa...")
    
    if selected_channel or search_q:
        try:
            params = {"limit": 15}
            if selected_channel:
                params["channel"] = selected_channel
            if search_q:
                params["q"] = search_q
                
            response = requests.get(f"{API_BASE_URL}/grid/lookup", params=params)
            if response.status_code == 200:
                results = response.json().get("items", [])
                if results:
                    for res in results:
                        col_prog, col_btn = st.columns([3, 1])
                        with col_prog:
                            st.write(f"**{res['program_name']}** ({res['channel']}) - {res['start_time']} até {res['end_time']}")
                        with col_btn:
                            if st.button(f"Add", key=res['id'], use_container_width=True):
                                new_rule = {
                                    "channel": res['channel'],
                                    "program_name": res['program_name'],
                                    "start_time": res['start_time'],
                                    "end_time": res['end_time'],
                                    "days_of_week": [1,2,3,4,5]
                                }
                                st.session_state.temp_rules.append(new_rule)
                                st.rerun()
                else:
                    st.warning("Nenhum programa encontrado.")
        except Exception as e:
            st.error(f"{L['msg_connection_error']} {e}")

    if st.session_state.temp_rules:
        st.write("### Rules Selected")
        for i, r in enumerate(st.session_state.temp_rules):
            col_r1, col_r2 = st.columns([4, 1])
            with col_r1:
                st.write(f"**{r['channel']}**: {r['program_name']} ({r['start_time']}-{r['end_time']})")
            with col_r2:
                if st.button("🗑️", key=f"del_rule_{i}"):
                    st.session_state.temp_rules.pop(i)
                    st.rerun()

    col_a, col_b = st.columns([1, 1])
    
    def save_set(status):
        # Revert status to awaiting_approval if editing, as requested by user
        if st.session_state.edit_id and status != "stand_by":
            status = "awaiting_approval"
        
        payload = {
            "name": st.session_state.set_name,
            "search_terms": st.session_state.temp_terms,
            "rules": st.session_state.temp_rules,
            "status": status,
            "audience_data_enabled": st.session_state.audience_enabled,
            "clip_context_seconds": st.session_state.context_secs
        }
        try:
            if st.session_state.edit_id:
                # If editing, force status back to awaiting_approval unless it's a draft
                if status != "stand_by":
                    payload["status"] = "awaiting_approval"
                res = requests.put(f"{API_BASE_URL}/sets/{st.session_state.edit_id}", json=payload)
            else:
                res = requests.post(f"{API_BASE_URL}/sets", json=payload)
                if res.status_code == 200 and status == "awaiting_approval":
                    set_id = res.json()['id']
                    requests.patch(f"{API_BASE_URL}/sets/{set_id}/status", params={"status": "awaiting_approval"})

            if res.status_code == 200:
                st.success(L['msg_saved'])
                # Reset
                st.session_state.temp_terms = []
                st.session_state.temp_rules = []
                st.session_state.set_name = ""
                st.session_state.edit_id = None
                st.session_state.show_form = False
                st.rerun()
            else:
                st.error(f"Error: {res.text}")
        except Exception as e:
            st.error(f"{L['msg_connection_error']} {e}")

    with col_a:
        if st.button(L['btn_save_draft'], type="secondary", use_container_width=True):
            save_set("stand_by")
            
    with col_b:
        if st.button(L['btn_submit'], type="primary", use_container_width=True):
            save_set("awaiting_approval")

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    st.markdown("""
        <div style='text-align: center; padding: 40px 0;'>
            <div style='background-color: #2563eb; color: white; width: 60px; height: 60px; border-radius: 15px; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; font-size: 30px; margin-bottom: 20px;'>M</div>
            <h1 style='color: #1e293b; margin: 0;'>Mentions On-Demand</h1>
            <p style='color: #64748b;'>Sistema IA de Monitoramento de TV</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        with st.container(border=True):
            st.subheader("Entrar")
            email = st.text_input("E-mail", placeholder="admin@mentions.com")
            password = st.text_input("Senha", type="password", placeholder="****")
            submit = st.button("Acessar Sistema", use_container_width=True, type="primary")
            
            if submit:
                if not email or not password:
                    st.warning("Preencha todos os campos.")
                else:
                    try:
                        res = requests.post(f"{API_BASE_URL}/auth/login", json={"email": email, "password": password})
                        if res.status_code == 200:
                            st.session_state.user = res.json()
                            st.session_state.logged_in = True
                            st.rerun()
                        else:
                            st.error("E-mail ou senha incorretos.")
                    except Exception as e:
                        st.error(f"Erro ao conectar com o servidor: {e}")
            
            st.markdown("<br><small style='color: #94a3b8; display: block; text-align: center;'>Versão 1.3.1 - Kantar Ibope Media</small>", unsafe_allow_html=True)
    st.stop()

# --- HEADER ---
user = st.session_state.user

st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f0f2f6; padding-bottom: 15px; margin-bottom: 25px;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="background-color: #2563eb; color: white; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 20px;">M</div>
            <h1 style="margin: 0; color: #1e293b; font-size: 24px; font-weight: bold;">{L['title']}</h1>
        </div>
    </div>
""", unsafe_allow_html=True)

# Flags (Language Switcher)
col_h1, col_h2, col_h3, col_h4 = st.columns([9, 1, 1, 1])
with col_h2:
    if st.button("🇬🇧", help="English", key="btn_en"): st.session_state.lang = "GB"; st.rerun()
with col_h3:
    if st.button("🇵🇹", help="Português", key="btn_pt"): st.session_state.lang = "PT"; st.rerun()
with col_h4:
    if st.button("🇪🇸", help="Español", key="btn_es"): st.session_state.lang = "ES"; st.rerun()

# --- SIDEBAR ---
st.sidebar.markdown(f"**Usuário:** {user['full_name']}<br><small>{user['role'].upper()}</small>", unsafe_allow_html=True)
if user['role'] == "client":
    # Use index to allow programmatic navigation
    if 'client_nav_index' not in st.session_state: st.session_state.client_nav_index = 0
    
    page_options = [L['nav_list'], L['nav_reports'], L['nav_test']]
    page = st.sidebar.radio(L['title'], page_options, index=st.session_state.client_nav_index, key="client_radio")
    
    # Update index if radio changed manually
    if st.session_state.client_nav_index != page_options.index(page):
        st.session_state.client_nav_index = page_options.index(page)
        st.session_state.show_form = False
        st.session_state.edit_id = None
        st.rerun()
elif user['role'] == "operator":
    op_pages = {
        L['op_nav_approvals']: "approvals",
        L['op_nav_health']: "health",
        L['op_nav_clients']: "clients"
    }
    page_label = st.sidebar.radio("Operador", list(op_pages.keys()))
    page = op_pages[page_label]
else: # admin
    page = st.sidebar.radio("Admin", ["Logs de Auditoria", "Configurações Globais", "Gestão de Usuários"])

st.sidebar.divider()
if st.sidebar.button(f"🚪 {L['btn_logout']}", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# --- PAGE: OPERATOR APPROVALS ---
if user['role'] == "operator" and page == "approvals":

    st.header(L['op_nav_approvals'])
    try:
        res = requests.get(f"{API_BASE_URL}/operator/pending-sets")
        if res.status_code == 200:
            pending = res.json()
            if not pending:
                st.info("Nenhum set aguardando aprovação.")
            else:
                for p in pending:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        col1.write(f"**{p['name']}**")
                        col1.caption(f"Cliente: {p['client_name']} ({p['client_company']})")
                        col2.write(f"⏱️ {p['total_minutes']} min/semana")
                        
                        # Credit logic
                        is_over_limit = p['total_minutes'] * 10 > p['client_credit_limit'] # Dummy math
                        if is_over_limit:
                            st.warning(f"⚠️ Limite de Crédito Excedido (Limite: {p['client_credit_limit']})")
                            justification = st.text_input("Quem aprovou extrapolar o limite?", key=f"just_{p['id']}")
                            if st.button("Aprovar com Justificativa", key=f"app_{p['id']}", disabled=not justification):
                                payload = {"action": "approve_set", "target_id": p['id'], "justification": justification}
                                requests.post(f"{API_BASE_URL}/operator/approve-set", json=payload)
                                st.rerun()
                        else:
                            if st.button("Aprovar", key=f"app_{p['id']}"):
                                payload = {"action": "approve_set", "target_id": p['id']}
                                requests.post(f"{API_BASE_URL}/operator/approve-set", json=payload)
                                st.rerun()
    except Exception as e:
        st.error(f"Erro: {e}")

# --- PAGE: SYSTEM HEALTH ---
elif user['role'] == "operator" and page == "health":
    st.header(L['op_nav_health'])
    try:
        res = requests.get(f"{API_BASE_URL}/operator/health")
        if res.status_code == 200:
            health = res.json()
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Clientes Ativos", health['active_clients'])
            c2.metric("Sets Configurados", health['active_sets'])
            c3.metric("Em Execução", health['running_now'])
            c4.metric("Próximos (Fila)", health['upcoming'])
            
            if health['errors'] > 0:
                st.error(f"🚨 {health['errors']} Erros de Execução Detectados!")
            else:
                st.success("✅ Todos os sistemas operando normalmente.")
            
            st.divider()
            st.subheader("Monitoring Sets no Sistema")
            sets_res = requests.get(f"{API_BASE_URL}/operator/sets")
            if sets_res.status_code == 200:
                all_sets = sets_res.json()
                for s in all_sets:
                    with st.container(border=True):
                        col_s1, col_s2, col_s3 = st.columns([3, 1, 1])
                        col_s1.write(f"**{s['name']}**")
                        col_s1.caption(f"Cliente: {s['client_name']} ({s['client_company']})")
                        col_s2.write(f"Status: `{s['status'].upper()}`")
                        if st.session_state.lang == "PT":
                            repro_btn = "Reprocessar"
                        elif st.session_state.lang == "GB":
                            repro_btn = "Reprocess"
                        else:
                            repro_btn = "Reprocesar"
                        
                        if col_s3.button(repro_btn, key=f"repro_{s['id']}"):
                            re_res = requests.post(f"{API_BASE_URL}/sets/{s['id']}/reprocess")
                            if re_res.status_code == 200:
                                st.toast(f"Reprocessamento agendado para: {s['name']}")
                            else:
                                st.error("Erro ao solicitar reprocessamento.")

    except Exception as e:
        st.error(f"Erro: {e}")

# --- PAGE: CUSTOMER MANAGEMENT ---
elif user['role'] == "operator" and page == "clients":
    st.header(L['op_nav_clients'])
    try:
        res = requests.get(f"{API_BASE_URL}/operator/clients")
        if res.status_code == 200:
            clients = res.json()
            for c in clients:
                with st.container(border=True):
                    col_c1, col_c2, col_c3 = st.columns([2, 1, 1])
                    with col_c1:
                        st.write(f"**{c['full_name']}**")
                        st.caption(f"Empresa: {c['company_name']} | Email: {c['email']}")
                        st.write(f"Limite: R$ {c['credit_limit']/100:.2f}")
                    
                    with col_c2:
                        st.write(f"**{L['lbl_active_sets']}:** {c['active_sets_count']}")
                        st.write(f"**{L['lbl_total_min']}:** {c['total_minutes_estimate']}")
                    
                    with col_c3:
                        if c['is_blocked_access']:
                            if st.button(L['btn_unblock'], key=f"unblock_{c['id']}", type="primary"):
                                requests.patch(f"{API_BASE_URL}/operator/user/{c['id']}/block", params={"block": False})
                                st.rerun()
                        else:
                            if st.button(L['btn_block'], key=f"block_{c['id']}", type="secondary"):
                                requests.patch(f"{API_BASE_URL}/operator/user/{c['id']}/block", params={"block": True})
                                st.rerun()
                        
                        # Credit adjustment expander
                        with st.popover(L['btn_adjust_credit']):
                            new_limit = st.number_input("Novo Limite (centavos)", value=c['credit_limit'], key=f"cred_val_{c['id']}")
                            if st.button("Confirmar", key=f"conf_cred_{c['id']}"):
                                requests.patch(f"{API_BASE_URL}/operator/user/{c['id']}/credit", params={"credit_limit": new_limit})
                                st.rerun()
    except Exception as e:
        st.error(f"Erro: {e}")

# --- PAGE: ADMIN LOGS ---
elif user['role'] == "admin" and page == "Logs de Auditoria":
    st.header("Logs de Auditoria (Read-only)")
    try:
        res = requests.get(f"{API_BASE_URL}/admin/logs")
        if res.status_code == 200:
            logs = res.json()
            if logs:
                df_logs = pd.DataFrame(logs)
                
                # Format timestamp
                df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
                
                # Rename and reorder columns for better reading
                # Columns: id, operator_id, operator_name, action, target_id, target_type, justification, timestamp
                df_view = df_logs[['timestamp', 'operator_name', 'action', 'justification', 'target_type']]
                df_view.columns = ['Data/Hora', 'Operador', 'Ação', 'Justificativa', 'Tipo Alvo']
                
                st.dataframe(df_view, use_container_width=True)
            else:
                st.info("Nenhum log registrado.")
    except Exception as e:
        st.error(f"Erro: {e}")

# --- PAGE: MY SETS ---
elif user['role'] == "client" and page == L['nav_list']:
    if st.session_state.show_form:
        render_monitoring_form()
    else:
        col_list_h1, col_list_h2 = st.columns([3, 1])
        with col_list_h1:
            st.header(L['header_list'])
        with col_list_h2:
            if st.button(L['btn_new_set'], type="primary", use_container_width=True):
                st.session_state.show_form = True
                st.session_state.edit_id = None
                st.session_state.set_name = ""
                st.session_state.temp_terms = []
                st.session_state.temp_rules = []
                st.session_state.audience_enabled = False
                st.session_state.context_secs = 15
                st.rerun()
        
        try:
            response = requests.get(f"{API_BASE_URL}/sets")
            if response.status_code == 200:
                monitoring_sets = response.json()
                if not monitoring_sets:
                    st.info(L['msg_no_sets'])
                else:
                    for s in monitoring_sets:
                        status_text = L.get(f"status_{s['status'].split('_')[0]}", s['status'].upper())
                        with st.expander(f"{s['name']} - Status: {status_text}"):
                            col_s1, col_s2 = st.columns([4, 1])
                            with col_s1:
                                st.write(f"**Tags:** {', '.join(s['search_terms'])}")
                            with col_s2:
                                # ACTIONS
                                col_act1, col_act2 = st.columns(2)
                                with col_act1:
                                    if st.button("✏️", key=f"edit_{s['id']}", help="Edit"):
                                        st.session_state.edit_id = s['id']
                                        st.session_state.set_name = s['name']
                                        st.session_state.temp_terms = s['search_terms']
                                        st.session_state.temp_rules = s['rules']
                                        st.session_state.audience_enabled = s.get('audience_data_enabled', False)
                                        st.session_state.context_secs = s.get('clip_context_seconds', 15)
                                        st.session_state.show_form = True
                                        st.rerun()
                                with col_act2:
                                    if st.button("🗑️", key=f"delete_{s['id']}", help="Delete"):
                                        requests.delete(f"{API_BASE_URL}/sets/{s['id']}")
                                        st.success(L['msg_deleted'])
                                        st.rerun()

                            # Check for report config
                            try:
                                conf_res = requests.get(f"{API_BASE_URL}/reports/config/{s['id']}")
                                if conf_res.status_code == 200 and conf_res.json():
                                    c = conf_res.json()
                                    f_label = L.get(f"freq_{c['frequency']}", c['frequency'].upper())
                                    st.caption(f"📅 Relatório: {f_label} às {c['hour']}:00h")
                                else:
                                    if s['status'] in ['approved', 'active']:
                                        st.markdown("<span style='color: #ef4444; font-weight: bold; font-size: 13px;'>⚠️ Pendente configuração de envio do relatório</span>", unsafe_allow_html=True)
                            except:
                                pass

                            if s['rules']:
                                st.write(f"**{L['th_program']}:**")
                                df_rules = pd.DataFrame(s['rules'])[['channel', 'program_name', 'start_time', 'end_time']]
                                st.table(df_rules)
                            
                            st.divider()
                            st.subheader(L['btn_load_mentions'])
                            if st.button(L['btn_load_mentions'], key=f"load_{s['id']}"):
                                m_res = requests.get(f"{API_BASE_URL}/sets/{s['id']}/mentions")
                                if m_res.status_code == 200:
                                    mentions = m_res.json()
                                    if not mentions:
                                        st.info(L['msg_no_mentions'])
                                    else:
                                        for m in mentions:
                                            with st.container(border=True):
                                                st.write(f"**{m['program_name']}** ({m['channel']})")
                                                occ_time = pd.to_datetime(m['occurrence_time']).strftime('%Y-%m-%d %H:%M')
                                                st.write(f"🕒 {occ_time}")
                                                st.info(f"💬 {m['transcription']}")
                                                if m['video_url']:
                                                    st.link_button("Clipe", m['video_url'])

                            if st.button(L['btn_sim_mention'], key=f"sim_{s['id']}"):
                                payload = {
                                    "channel": s['rules'][0]['channel'] if s['rules'] else "Globo",
                                    "program_name": s['rules'][0]['program_name'] if s['rules'] else "Jornal Nacional",
                                    "occurrence_time": datetime.now().isoformat(),
                                    "transcription": f"O termo '{s['search_terms'][0]}' foi mencionado durante a transmissão.",
                                    "context": "Simulação de detecção via LLM.",
                                    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                                }
                                requests.post(f"{API_BASE_URL}/sets/{s['id']}/mentions", json=payload)
                                st.rerun()

                            if s['status'] == 'stand_by':
                                if st.button(f"Submit for Approval", key=f"sub_{s['id']}"):
                                    requests.patch(f"{API_BASE_URL}/sets/{s['id']}/status", params={"status": "awaiting_approval"})
                                    st.rerun()
            else:
                st.error(f"{L['msg_connection_error']} {response.text}")
        except Exception as e:
            st.error(f"{L['msg_connection_error']} {e}")

# --- PAGE: REPORTS & BILLING ---
elif user['role'] == "client" and page == L['nav_reports']:
    st.header(L['header_reports'])
    
    tab1, tab2, tab3 = st.tabs([L['nav_reports'].split(' ')[0], L['header_billing'], L['tab_occurrences']])
    
    with tab1:
        st.subheader("Configuração de Relatórios Automáticos")
        
        # Select monitoring set for config
        try:
            sets_res = requests.get(f"{API_BASE_URL}/sets")
            if sets_res.status_code == 200:
                monitoring_sets = sets_res.json()
                if monitoring_sets:
                    set_options = {s['name']: s['id'] for s in monitoring_sets}
                    selected_set_name = st.selectbox("Selecione o Conjunto para Configurar", options=list(set_options.keys()))
                    selected_set_id = set_options[selected_set_name]
                    
                    if 'last_selected_set_id' not in st.session_state or st.session_state.last_selected_set_id != selected_set_id:
                        st.session_state.last_selected_set_id = selected_set_id
                        st.session_state.report_edit_mode = False
                        st.rerun()
                    
                    # Fetch existing config
                    config_res = requests.get(f"{API_BASE_URL}/reports/config/{selected_set_id}")
                    existing_config = config_res.json() if config_res.status_code == 200 else None
                    
                    if existing_config:
                        freq_label = L.get(f"freq_{existing_config['frequency']}", existing_config['frequency'].upper())
                        st.success(f"✅ **{L['nav_reports'].split(' ')[0]} {L['th_status']}:** {freq_label} às **{existing_config['hour']}:00h**")
                        st.caption(f"📧 Destinatários: `{', '.join(existing_config['email_recipients'])}`")
                        
                        if not st.session_state.report_edit_mode:
                            if st.button(L['btn_edit_config'], use_container_width=True):
                                st.session_state.report_edit_mode = True
                                st.rerun()
                    else:
                        st.error(f"⚠️ **{L['status_stand_by'].split('-')[0].capitalize()}**: Pendente configuração de envio do relatório")

                    if not existing_config or st.session_state.report_edit_mode:
                        with st.form("report_config_form"):
                            options = ["daily", "weekly", "monthly"]
                            freq = st.selectbox(L['label_frequency'], options, 
                                                format_func=lambda x: L.get(f"freq_{x}", x),
                                                index=options.index(existing_config['frequency']) if existing_config else 0)
                            hour = st.number_input(L['label_hour'], 0, 23, value=existing_config['hour'] if existing_config else 8)
                            recipients = st.text_input(L['label_recipients'], value=", ".join(existing_config['email_recipients']) if existing_config else "")
                            
                            c_f1, c_f2 = st.columns(2)
                            with c_f1:
                                if st.form_submit_button(L['btn_save_config'], use_container_width=True):
                                    payload = {
                                        "monitoring_set_id": selected_set_id,
                                        "frequency": freq,
                                        "hour": hour,
                                        "email_recipients": [r.strip() for r in recipients.split(",") if r.strip()]
                                    }
                                    save_res = requests.post(f"{API_BASE_URL}/reports/config", json=payload)
                                    if save_res.status_code == 200:
                                        st.success(L['msg_saved'])
                                        st.session_state.report_edit_mode = False
                                        st.rerun()
                                    else:
                                        st.error(f"Erro ao salvar: {save_res.text}")
                            with c_f2:
                                if st.session_state.report_edit_mode:
                                    if st.form_submit_button(L['btn_cancel'], use_container_width=True):
                                        st.session_state.report_edit_mode = False
                                        st.rerun()
                    
                    st.divider()
                    st.subheader("Histórico de Relatórios")
                    hist_res = requests.get(f"{API_BASE_URL}/reports/history/{selected_set_id}")
                    if hist_res.status_code == 200:
                        history = hist_res.json()
                        if history:
                            df_hist = pd.DataFrame(history)
                            # Format dates
                            for col in ['generated_at', 'period_start', 'period_end']:
                                df_hist[col] = pd.to_datetime(df_hist[col]).dt.strftime('%Y-%m-%d %H:%M')
                            
                            df_hist = df_hist[['generated_at', 'period_start', 'period_end', 'file_url']]
                            df_hist.columns = [L['th_date'], 'Início', 'Fim', 'Link']
                            st.dataframe(df_hist, use_container_width=True)
                        else:
                            st.info("Nenhum relatório gerado ainda.")
                else:
                    st.warning(L['msg_no_sets'])
        except Exception as e:
            st.error(f"Erro: {e}")

    with tab2:
        st.subheader(L['header_billing'])
        try:
            inv_res = requests.get(f"{API_BASE_URL}/invoices")
            if inv_res.status_code == 200:
                invoices = inv_res.json()
                if invoices:
                    for inv in invoices:
                        with st.container(border=True):
                            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                            c1.write(f"**Período:** {inv['billing_period']}")
                            c2.write(f"**{L['th_amount']}:** R$ {inv['amount']/100:.2f}")
                            c3.write(f"**{L['th_due']}:** {inv['due_date']}")
                            status_color = "green" if inv['status'] == "paid" else "red"
                            c4.markdown(f"<span style='color: {status_color}; font-weight: bold;'>{inv['status'].upper()}</span>", unsafe_allow_html=True)
                            if inv['pdf_url']:
                                st.link_button("Download PDF", inv['pdf_url'], size="small")
                else:
                    st.info("Nenhuma fatura encontrada.")
        except Exception as e:
            st.error(f"Erro ao carregar faturas: {e}")

    with tab3:
        st.header(L['header_reports'])
        # (Existing mentions logic moved here)
        try:
            response = requests.get(f"{API_BASE_URL}/mentions", params={"limit": 50})
            if response.status_code == 200:
                mentions = response.json()
                if not mentions:
                    st.info(L['msg_no_mentions'])
                else:
                    for m in mentions:
                        with st.container(border=True):
                            col_m1, col_m2 = st.columns([3, 1])
                            with col_m1:
                                st.subheader(f"{m['program_name']}")
                                st.write(f"**{L['th_channel']}:** {m['channel']}")
                                occ_time = pd.to_datetime(m['occurrence_time']).strftime('%Y-%m-%d %H:%M')
                                st.write(f"🕒 {occ_time}")
                            with col_m2:
                                if m['video_url']:
                                    st.link_button("Clipe", m['video_url'], use_container_width=True)
                            st.info(f"💬 {m['transcription']}")
                            if m['context']:
                                st.caption(f"Contexto: {m['context']}")
        except Exception as e:
            st.error(f"{L['msg_connection_error']} {e}")

# --- PAGE: TEST EMAIL ---
elif user['role'] == "client" and page == L['nav_test']:
    st.header(L['header_test'])
    # ... (email test logic remains same)
    email_dest = st.text_input("Email", value="eduardo.fonseca.na@gmail.com")
    if st.button("Send Test"):
        with st.spinner("Sending..."):
            try:
                res = email_service.send_notification(to=email_dest, subject="Test", text="Mentions On-Demand Test")
                st.success("Sent!")
            except Exception as e:
                st.error(str(e))

