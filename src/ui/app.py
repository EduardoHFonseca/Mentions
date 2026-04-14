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
        "adm_nav_logs": "Audit Logs",
        "adm_nav_config": "Global Config",
        "adm_nav_users": "User Management",
        "lbl_active_sets": "Active Sets",
        "lbl_total_min": "Total Min/Week",
        "btn_reprocess": "Reprocess",
        "btn_block": "Block",
        "btn_unblock": "Unblock",
        "btn_adjust_credit": "Adjust Credit",
        "lbl_contact": "contact",
        "lbl_credit": "Limit",
        "lbl_search": "Search Agency",
        "lbl_status_filter": "Status",
        "filter_all": "All",
        "filter_active": "Active",
        "filter_blocked": "Blocked",
        "filter_pending": "Pending",
        "btn_edit_user": "Edit Info",
        "btn_add_client": "Add Client",

        "lbl_razao_social": "Corporate Name",
        "lbl_cnpj": "CNPJ",
        "lbl_address": "Address",
        "lbl_phone": "Phone",
        "lbl_email": "Email",
        "lbl_password": "Password",
        "btn_delete": "Delete",
        "msg_confirm_delete": "Are you sure you want to delete this client?"
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
        "adm_nav_logs": "Logs de Auditoria",
        "adm_nav_config": "Configurações Globais",
        "adm_nav_users": "Gestão de Usuários",
        "lbl_active_sets": "Sets Ativos",
        "lbl_total_min": "Total Min/Semana",
        "btn_reprocess": "Reprocessar",
        "btn_block": "Bloquear",
        "btn_unblock": "Desbloquear",
        "btn_adjust_credit": "Ajustar Crédito",
        "lbl_contact": "contato",
        "lbl_credit": "Limite",
        "lbl_search": "Buscar Agência",
        "lbl_status_filter": "Status",
        "filter_all": "Todos",
        "filter_active": "Ativos",
        "filter_blocked": "Bloqueados",
        "filter_pending": "Pendentes",
        "btn_edit_user": "Editar Info",
        "btn_add_client": "Novo Cliente",

        "lbl_razao_social": "Razão Social",
        "lbl_cnpj": "CNPJ",
        "lbl_address": "Endereço",
        "lbl_phone": "Telefone",
        "lbl_email": "E-mail",
        "lbl_password": "Senha",
        "btn_delete": "Excluir",
        "msg_confirm_delete": "Tem certeza que deseja excluir este cliente?"
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
        "adm_nav_logs": "Logs de Auditoría",
        "adm_nav_config": "Configuración Global",
        "adm_nav_users": "Gestión de Usuarios",
        "lbl_contact": "contacto",
        "lbl_credit": "Límite",
        "lbl_search": "Buscar Agencia",
        "lbl_status_filter": "Estado",
        "filter_all": "Todos",
        "filter_active": "Activos",
        "filter_blocked": "Bloqueados",
        "filter_pending": "Pendientes",
        "btn_edit_user": "Editar Info",
        "btn_add_client": "Nuevo Cliente",

        "lbl_razao_social": "Razón Social",
        "lbl_cnpj": "CNPJ",
        "lbl_address": "Dirección",
        "lbl_phone": "Teléfono",
        "lbl_email": "E-mail",
        "lbl_password": "Contraseña",
        "btn_delete": "Eliminar",
        "msg_confirm_delete": "¿Está seguro de que deseja eliminar este cliente?",
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
if 'show_register' not in st.session_state: st.session_state.show_register = False

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
            set_name = st.text_input(L['label_name'], value=st.session_state.set_name, placeholder="Ex.: Clipping da Concorrência")
            st.session_state.set_name = set_name
            
            st.write("---")
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
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
    
    channels = []
    try:
        channels_res = requests.get(f"{API_BASE_URL}/grid/channels")
        if channels_res.status_code == 200:
            channels = sorted(channels_res.json())
    except:
        st.error("Erro ao carregar canais.")

    selected_channel = st.selectbox(L['label_channel'], options=[""] + channels)
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
        user_id_param = {"user_id": st.session_state.user['id']}
        try:
            if st.session_state.edit_id:
                if status != "stand_by":
                    payload["status"] = "awaiting_approval"
                res = requests.put(f"{API_BASE_URL}/sets/{st.session_state.edit_id}", json=payload)
            else:
                res = requests.post(f"{API_BASE_URL}/sets", json=payload, params=user_id_param)
                if res.status_code == 200 and status == "awaiting_approval":
                    set_id = res.json()['id']
                    requests.patch(f"{API_BASE_URL}/sets/{set_id}/status", params={"status": "awaiting_approval"})

            if res.status_code == 200:
                st.success(L['msg_saved'])
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

if 'reg_success' not in st.session_state: st.session_state.reg_success = False

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
        if not st.session_state.show_register:
            with st.container(border=True):
                st.subheader("Entrar")
                email = st.text_input("E-mail", placeholder="contato@pixelwave.com")
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
                                st.session_state.client_nav_index = 0
                                st.session_state.show_form = False
                                st.rerun()
                            elif res.status_code == 403:
                                st.warning(res.json().get("detail", "Acesso restrito."))
                            else:
                                st.error("E-mail ou senha incorretos.")
                        except Exception as e:
                            st.error(f"Erro ao conectar com o servidor: {e}")
                
                st.write("---")
                if st.button("É novo aqui? Cadastre-se", use_container_width=True):
                    st.session_state.show_register = True
                    st.session_state.reg_success = False
                    st.rerun()
        else:
            with st.container(border=True):
                if st.session_state.reg_success:
                    st.success("Cadastro realizado com sucesso!")
                    st.info("Sua conta está aguardando aprovação pelo operador. Você receberá um aviso assim que puder acessar.")
                    if st.button("Voltar para o Login", use_container_width=True):
                        st.session_state.show_register = False
                        st.session_state.reg_success = False
                        st.rerun()
                else:
                    st.subheader("Novo Cadastro")
                    with st.form("public_register_form"):
                        reg_company = st.text_input("Nome Fantasia", placeholder="Sua Agência")
                        reg_razao = st.text_input("Razão Social")
                        reg_cnpj = st.text_input("CNPJ")
                        reg_name = st.text_input("Nome do Contato")
                        reg_email = st.text_input("E-mail")
                        reg_pass = st.text_input("Senha", type="password")
                        reg_phone = st.text_input("Telefone")
                        reg_address = st.text_area("Endereço")
                        
                        st.caption("Ao se cadastrar, sua conta passará por uma aprovação prévia.")
                        
                        col_reg1, col_reg2 = st.columns(2)
                        with col_reg1:
                            reg_submit = st.form_submit_button("Finalizar Cadastro", type="primary", use_container_width=True)
                        with col_reg2:
                            if st.form_submit_button("Cancelar", use_container_width=True):
                                st.session_state.show_register = False
                                st.rerun()
                        
                        if reg_submit:
                            if not reg_email or not reg_pass or not reg_company:
                                st.error("Campos obrigatórios: Nome Fantasia, E-mail e Senha.")
                            else:
                                payload = {
                                    "full_name": reg_name,
                                    "email": reg_email,
                                    "password": reg_pass,
                                    "company_name": reg_company,
                                    "billing_info": {
                                        "razao_social": reg_razao,
                                        "cnpj": reg_cnpj,
                                        "telefone": reg_phone,
                                        "endereco": reg_address
                                    }
                                }
                                try:
                                    res = requests.post(f"{API_BASE_URL}/auth/register", json=payload)
                                    if res.status_code in [200, 201]:
                                        st.session_state.reg_success = True
                                        st.rerun()
                                    else:
                                        st.error(f"Erro no cadastro: {res.text}")
                                except Exception as e:
                                    st.error(f"Erro de conexão: {e}")
            
            if not st.session_state.reg_success:
                if st.button("Voltar", key="back_from_reg"):
                    st.session_state.show_register = False
                    st.rerun()

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

# --- SIDEBAR ---
st.sidebar.markdown(f"**Usuário:** {user['full_name']}<br><small>{user['role'].upper()}</small>", unsafe_allow_html=True)

# Language Switcher in Sidebar
with st.sidebar:
    st.write("---")
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        if st.button("🇬🇧", help="English", key="btn_en"): st.session_state.lang = "GB"; st.rerun()
    with col_l2:
        if st.button("🇵🇹", help="Português", key="btn_pt"): st.session_state.lang = "PT"; st.rerun()
    with col_l3:
        if st.button("🇪🇸", help="Español", key="btn_es"): st.session_state.lang = "ES"; st.rerun()
    st.write("---")

if user['role'] == "client":
    if 'client_nav_index' not in st.session_state: st.session_state.client_nav_index = 0
    page_options = [L['nav_list'], L['nav_reports'], L['nav_test']]
    page = st.sidebar.radio(L['title'], page_options, index=st.session_state.client_nav_index, key="client_radio")
    
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
    adm_pages = {
        L['adm_nav_logs']: "logs",
        L['adm_nav_config']: "config",
        L['adm_nav_users']: "users"
    }
    page_label = st.sidebar.radio("Admin", list(adm_pages.keys()))
    page = adm_pages[page_label]

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
                        with col1:
                            st.write(f"**{p['client_company']}**")
                            st.caption(f"Set: {p['name']}")
                        
                        with col2:
                            job_value = p['total_minutes'] * 10 # Example: 10 cents per minute
                            st.write(f"⏱️ {p['total_minutes']} min")
                            st.write(f"💰 **R$ {job_value/100:.2f}**")
                        
                        with col3:
                            # Credit logic
                            is_over_limit = job_value > p['client_credit_limit']
                            if is_over_limit:
                                st.warning(f"⚠️ Limite Excedido (Saldo: R$ {p['client_credit_limit']/100:.2f})")
                                justification = st.text_input("Justificativa de aprovação", key=f"just_{p['id']}")
                                if st.button("Aprovar c/ Exceção", key=f"app_{p['id']}", disabled=not justification, use_container_width=True):
                                    payload = {"action": "approve_set", "target_id": p['id'], "justification": justification}
                                    requests.post(f"{API_BASE_URL}/operator/approve-set", json=payload)
                                    st.rerun()
                            else:
                                if st.button("Aprovar Set", key=f"app_{p['id']}", type="primary", use_container_width=True):
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
                        repro_btn = "Reprocessar" if st.session_state.lang == "PT" else ("Reprocess" if st.session_state.lang == "GB" else "Reprocesar")
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
        if 'op_client_mode' not in st.session_state: st.session_state.op_client_mode = 'list'
        if 'selected_client' not in st.session_state: st.session_state.selected_client = None

        if st.session_state.op_client_mode == 'list':
            col_h1, col_h2 = st.columns([3, 1])
            with col_h2:
                if st.button(L['btn_add_client'], type="primary", use_container_width=True):
                    st.session_state.op_client_mode = 'add'
                    st.rerun()

            res = requests.get(f"{API_BASE_URL}/operator/clients")
            if res.status_code == 200:
                clients = res.json()
                col_f1, col_f2 = st.columns([2, 1])
                search_query = col_f1.text_input(L['lbl_search'], key="client_search")
                status_filter = col_f2.radio(L['lbl_status_filter'], [L['filter_all'], L['filter_active'], L['filter_blocked'], L['filter_pending']], horizontal=True)
                filtered_clients = clients
                if search_query:
                    search_query = search_query.lower()
                    filtered_clients = [c for c in filtered_clients if search_query in c['company_name'].lower() or search_query in c['full_name'].lower() or (c['billing_info'] and c['billing_info'].get('cnpj') and search_query in c['billing_info']['cnpj'])]
                if status_filter == L['filter_active']:
                    filtered_clients = [c for c in filtered_clients if not c['is_blocked_access'] and c['status'] == 'approved']
                elif status_filter == L['filter_blocked']:
                    filtered_clients = [c for c in filtered_clients if c['is_blocked_access']]
                elif status_filter == L['filter_pending']:
                    filtered_clients = [c for c in filtered_clients if c['status'] == 'pending_approval']

                # Sort by Company Name (Alphabetical)
                filtered_clients = sorted(filtered_clients, key=lambda x: x['company_name'].lower())

                col_th1, col_th2, col_th3, col_th4, col_th5 = st.columns([2, 2, 1, 1, 1])
                col_th1.write("**Empresa / CNPJ**")
                col_th2.write("**Contato / E-mail**")
                col_th3.write("**Crédito**")
                col_th4.write("**Sets**")
                col_th5.write("**Ações**")
                st.divider()

                for c in filtered_clients:
                    col_tr1, col_tr2, col_tr3, col_tr4, col_tr5 = st.columns([2, 2, 1, 1, 1])
                    cnpj = c['billing_info'].get('cnpj', 'N/A') if c['billing_info'] else 'N/A'
                    col_tr1.write(f"**{c['company_name']}**")
                    col_tr1.caption(f"CNPJ: {cnpj}")
                    col_tr2.write(c['full_name'])
                    col_tr2.caption(f"{c['email']}")
                    col_tr3.write(f"R$ {c['credit_limit']/100:.2f}")
                    col_tr4.write(f"{c['active_sets_count']} / {c['total_minutes_estimate']}m")
                    with col_tr5:
                        if st.button("👁️", key=f"view_{c['id']}", help="Detalhes"):
                            st.session_state.selected_client = c
                            st.session_state.op_client_mode = 'edit'
                            st.rerun()
                        lock_icon = "🔓" if c['is_blocked_access'] else "🚫"
                        if st.button(lock_icon, key=f"quick_block_{c['id']}"):
                            requests.patch(f"{API_BASE_URL}/operator/user/{c['id']}/block", params={"block": not c['is_blocked_access']})
                            st.rerun()

        elif st.session_state.op_client_mode in ['add', 'edit']:
            is_edit = st.session_state.op_client_mode == 'edit'
            client = st.session_state.selected_client if is_edit else {}
            billing = client.get('billing_info', {}) if is_edit and client.get('billing_info') else {}
            st.subheader("Dados do Cliente" if is_edit else "Novo Cliente")
            with st.form("client_form"):
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    f_company = st.text_input("Nome Fantasia", value=client.get('company_name', ''))
                    f_razao = st.text_input("Razão Social", value=billing.get('razao_social', ''))
                    f_cnpj = st.text_input("CNPJ", value=billing.get('cnpj', ''))
                with col_f2:
                    f_name = st.text_input("Nome do Contato", value=client.get('full_name', ''))
                    f_email = st.text_input("Email", value=client.get('email', ''), disabled=is_edit)
                    f_pass = st.text_input("Senha", type="password", value="1234")
                    f_phone = st.text_input("Telefone", value=billing.get('telefone', ''))
                f_address = st.text_area("Endereço", value=billing.get('endereco', ''))
                col_f3, col_f4 = st.columns(2)
                f_limit = col_f3.number_input("Limite de Crédito (R$)", value=float(client.get('credit_limit', 500000)/100.0), step=50.0)
                f_status = col_f4.selectbox("Status", ["approved", "pending_approval", "blocked"], index=0 if client.get('status') == "approved" else 1)
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
                with col_btn1:
                    submitted = st.form_submit_button("Salvar", type="primary")
                with col_btn2:
                    if st.form_submit_button("Cancelar"):
                        st.session_state.op_client_mode = 'list'
                        st.rerun()
                if submitted:
                    payload = {
                        "full_name": f_name,
                        "company_name": f_company,
                        "credit_limit": int(f_limit * 100),
                        "status": f_status,
                        "billing_info": {"razao_social": f_razao, "cnpj": f_cnpj, "endereco": f_address, "telefone": f_phone}
                    }
                    if is_edit:
                        payload["password"] = f_pass # Operator can change password
                        res = requests.patch(f"{API_BASE_URL}/operator/user/{client['id']}", json=payload)
                    else:
                        payload["email"] = f_email
                        payload["password"] = f_pass
                        res = requests.post(f"{API_BASE_URL}/operator/user", json=payload)
                    if res.status_code in [200, 201]:
                        st.success("Cliente salvo!")
                        st.session_state.op_client_mode = 'list'
                        st.rerun()
                    else:
                        st.error(f"Erro: {res.text}")
            if is_edit:
                with st.expander("Zona de Perigo"):
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        if st.button("Limpar Todos os Monitoramentos", type="secondary", use_container_width=True):
                            res = requests.delete(f"{API_BASE_URL}/operator/user/{client['id']}/sets")
                            if res.status_code == 200:
                                st.success("Todos os monitoramentos foram removidos.")
                                st.rerun()
                            else:
                                st.error("Erro ao remover monitoramentos.")
                    with col_d2:
                        if st.button("Excluir Cliente Permanentemente", type="primary", use_container_width=True):
                            if requests.delete(f"{API_BASE_URL}/operator/user/{client['id']}").status_code == 200:
                                st.session_state.op_client_mode = 'list'; st.rerun()
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
                df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
                df_view = df_logs[['timestamp', 'operator_name', 'action', 'justification', 'target_type']]
                df_view.columns = ['Data/Hora', 'Operador', 'Ação', 'Justificativa', 'Tipo Alvo']
                st.dataframe(df_view, use_container_width=True)
            else:
                st.info("Nenhum log registrado.")
    except Exception as e:
        st.error(f"Erro: {e}")

# --- PAGE: ADMIN USER MANAGEMENT ---
elif user['role'] == "admin" and page == "users":
    st.header(L['adm_nav_users'])
    
    if 'adm_user_mode' not in st.session_state: st.session_state.adm_user_mode = 'list'
    if 'selected_adm_user' not in st.session_state: st.session_state.selected_adm_user = None

    if st.session_state.adm_user_mode == 'list':
        col_h1, col_h2 = st.columns([3, 1])
        with col_h2:
            if st.button("+ Novo Usuário Interno", type="primary", use_container_width=True):
                st.session_state.adm_user_mode = 'add'
                st.rerun()

        try:
            res = requests.get(f"{API_BASE_URL}/admin/users")
            if res.status_code == 200:
                users_list = res.json()
                
                # Sorting
                users_list = sorted(users_list, key=lambda x: x['full_name'].lower())

                col_th1, col_th2, col_th3, col_th4 = st.columns([2, 2, 1, 1])
                col_th1.write("**Nome Completo**")
                col_th2.write("**E-mail**")
                col_th3.write("**Perfil**")
                col_th4.write("**Ações**")
                st.divider()

                for u in users_list:
                    col_tr1, col_tr2, col_tr3, col_tr4 = st.columns([2, 2, 1, 1])
                    
                    status_prefix = "🚫 " if u['is_blocked_access'] else ""
                    col_tr1.write(f"{status_prefix}**{u['full_name']}**")
                    col_tr2.write(u['email'])
                    col_tr3.write(f"`{u['role'].upper()}`")
                    
                    with col_tr4:
                        if st.button("👁️", key=f"view_adm_{u['id']}", help="Editar"):
                            st.session_state.selected_adm_user = u
                            st.session_state.adm_user_mode = 'edit'
                            st.rerun()
                        
                        lock_icon = "🔓" if u['is_blocked_access'] else "🚫"
                        if st.button(lock_icon, key=f"block_adm_{u['id']}"):
                            requests.patch(f"{API_BASE_URL}/operator/user/{u['id']}/block", params={"block": not u['is_blocked_access']})
                            st.rerun()

        except Exception as e:
            st.error(f"Erro: {e}")

    elif st.session_state.adm_user_mode in ['add', 'edit']:
        is_edit = st.session_state.adm_user_mode == 'edit'
        u_data = st.session_state.selected_adm_user if is_edit else {}

        st.subheader("Dados do Usuário" if is_edit else "Novo Usuário Interno")
        
        with st.form("adm_user_form"):
            f_name = st.text_input("Nome Completo", value=u_data.get('full_name', ''))
            f_email = st.text_input("Email", value=u_data.get('email', ''), disabled=is_edit)
            f_pass = st.text_input("Senha", type="password", value="1234")
            f_role = st.selectbox("Perfil", ["operator", "admin"], index=0 if u_data.get('role') == "operator" else 1)
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
            with col_btn1:
                submitted = st.form_submit_button("Salvar", type="primary")
            with col_btn2:
                if st.form_submit_button("Cancelar"):
                    st.session_state.adm_user_mode = 'list'
                    st.rerun()
            
            if submitted:
                payload = {
                    "full_name": f_name,
                    "password": f_pass,
                    "role": f_role
                }
                
                if is_edit:
                    res = requests.patch(f"{API_BASE_URL}/operator/user/{u_data['id']}", json=payload)
                else:
                    payload["email"] = f_email
                    res = requests.post(f"{API_BASE_URL}/admin/user", json=payload)
                
                if res.status_code in [200, 201]:
                    st.success("Usuário salvo com sucesso!")
                    st.session_state.adm_user_mode = 'list'
                    st.rerun()
                else:
                    st.error(f"Erro ao salvar: {res.text}")

        if is_edit:
            st.divider()
            with st.expander("Zona de Perigo"):
                if st.button("Excluir Usuário Permanentemente", type="primary"):
                    res = requests.delete(f"{API_BASE_URL}/operator/user/{u_data['id']}")
                    if res.status_code == 200:
                        st.success("Usuário excluído.")
                        st.session_state.adm_user_mode = 'list'
                        st.rerun()
                    else:
                        st.error("Erro ao excluir.")

# --- PAGE: MY SETS ---
elif user['role'] == "client" and page == L['nav_list']:
    if st.session_state.show_form:
        render_monitoring_form()
    else:
        col_list_h1, col_list_h2 = st.columns([3, 1])
        with col_list_h1: st.header(L['header_list'])
        with col_list_h2:
            if st.button(L['btn_new_set'], type="primary", use_container_width=True):
                st.session_state.show_form = True; st.session_state.edit_id = None; st.session_state.set_name = ""
                st.session_state.temp_terms = []; st.session_state.temp_rules = []
                st.session_state.audience_enabled = False; st.session_state.context_secs = 15; st.rerun()
        try:
            response = requests.get(f"{API_BASE_URL}/sets", params={"user_id": user['id']})
            if response.status_code == 200:
                monitoring_sets = response.json()
                if not monitoring_sets: st.info(L['msg_no_sets'])
                else:
                    for s in monitoring_sets:
                        status_text = L.get(f"status_{s['status'].split('_')[0]}", s['status'].upper())
                        with st.expander(f"{s['name']} - Status: {status_text}"):
                            col_s1, col_s2 = st.columns([4, 1])
                            with col_s1: st.write(f"**Tags:** {', '.join(s['search_terms'])}")
                            with col_s2:
                                col_act1, col_act2 = st.columns(2)
                                with col_act1:
                                    if st.button("✏️", key=f"edit_{s['id']}"):
                                        st.session_state.edit_id = s['id']; st.session_state.set_name = s['name']
                                        st.session_state.temp_terms = s['search_terms']; st.session_state.temp_rules = s['rules']
                                        st.session_state.audience_enabled = s.get('audience_data_enabled', False)
                                        st.session_state.context_secs = s.get('clip_context_seconds', 15); st.session_state.show_form = True; st.rerun()
                                with col_act2:
                                    if st.button("🗑️", key=f"delete_{s['id']}"):
                                        requests.delete(f"{API_BASE_URL}/sets/{s['id']}"); st.rerun()
                            try:
                                conf_res = requests.get(f"{API_BASE_URL}/reports/config/{s['id']}")
                                if conf_res.status_code == 200 and conf_res.json():
                                    c = conf_res.json(); f_label = L.get(f"freq_{c['frequency']}", c['frequency'].upper())
                                    st.caption(f"📅 Relatório: {f_label} às {c['hour']}:00h")
                                elif s['status'] in ['approved', 'active']:
                                    st.markdown("<span style='color: #ef4444; font-weight: bold; font-size: 13px;'>⚠️ Pendente configuração de envio do relatório</span>", unsafe_allow_html=True)
                            except: pass
                            if s['rules']:
                                st.write(f"**{L['th_program']}:**")
                                df_rules = pd.DataFrame(s['rules'])[['channel', 'program_name', 'start_time', 'end_time']]
                                st.table(df_rules)
                            st.divider(); st.subheader(L['btn_load_mentions'])
                            if st.button(L['btn_load_mentions'], key=f"load_{s['id']}"):
                                m_res = requests.get(f"{API_BASE_URL}/sets/{s['id']}/mentions")
                                if m_res.status_code == 200:
                                    mentions = m_res.json()
                                    if not mentions: st.info(L['msg_no_mentions'])
                                    else:
                                        for m in mentions:
                                            with st.container(border=True):
                                                st.write(f"**{m['program_name']}** ({m['channel']})")
                                                occ_time = pd.to_datetime(m['occurrence_time']).strftime('%Y-%m-%d %H:%M')
                                                st.write(f"🕒 {occ_time}"); st.info(f"💬 {m['transcription']}")
                                                if m['video_url']: st.link_button("Clipe", m['video_url'])
                            if st.button(L['btn_sim_mention'], key=f"sim_{s['id']}"):
                                payload = {"channel": s['rules'][0]['channel'] if s['rules'] else "Globo", "program_name": s['rules'][0]['program_name'] if s['rules'] else "Jornal Nacional", "occurrence_time": datetime.now().isoformat(), "transcription": f"O termo '{s['search_terms'][0]}' foi mencionado.", "context": "Simulação.", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
                                requests.post(f"{API_BASE_URL}/sets/{s['id']}/mentions", json=payload); st.rerun()
                            if s['status'] == 'stand_by':
                                if st.button(f"Submit for Approval", key=f"sub_{s['id']}"):
                                    requests.patch(f"{API_BASE_URL}/sets/{s['id']}/status", params={"status": "awaiting_approval"}); st.rerun()
            else: st.error(f"{L['msg_connection_error']} {response.text}")
        except Exception as e: st.error(f"{L['msg_connection_error']} {e}")

# --- PAGE: REPORTS & BILLING ---
elif user['role'] == "client" and page == L['nav_reports']:
    st.header(L['header_reports'])
    tab1, tab2, tab3 = st.tabs([L['nav_reports'].split(' ')[0], L['header_billing'], L['tab_occurrences']])
    with tab1:
        st.subheader("Configuração de Relatórios Automáticos")
        try:
            sets_res = requests.get(f"{API_BASE_URL}/sets", params={"user_id": user['id']})
            if sets_res.status_code == 200:
                monitoring_sets = sets_res.json()
                if monitoring_sets:
                    set_options = {s['name']: s['id'] for s in monitoring_sets}
                    selected_set_name = st.selectbox("Selecione o Conjunto para Configurar", options=list(set_options.keys()))
                    selected_set_id = set_options[selected_set_name]
                    if 'last_selected_set_id' not in st.session_state or st.session_state.last_selected_set_id != selected_set_id:
                        st.session_state.last_selected_set_id = selected_set_id; st.session_state.report_edit_mode = False; st.rerun()
                    config_res = requests.get(f"{API_BASE_URL}/reports/config/{selected_set_id}")
                    existing_config = config_res.json() if config_res.status_code == 200 else None
                    if existing_config:
                        freq_label = L.get(f"freq_{existing_config['frequency']}", existing_config['frequency'].upper())
                        st.success(f"✅ **{L['nav_reports'].split(' ')[0]} {L['th_status']}:** {freq_label} às **{existing_config['hour']}:00h**")
                        st.caption(f"📧 Destinatários: `{', '.join(existing_config['email_recipients'])}`")
                        if not st.session_state.report_edit_mode:
                            if st.button(L['btn_edit_config'], use_container_width=True):
                                st.session_state.report_edit_mode = True; st.rerun()
                    else: st.error(f"⚠️ **{L['status_stand_by'].split('-')[0].capitalize()}**: Pendente configuração")
                    if not existing_config or st.session_state.report_edit_mode:
                        with st.form("report_config_form"):
                            options = ["daily", "weekly", "monthly"]
                            freq = st.selectbox(L['label_frequency'], options, format_func=lambda x: L.get(f"freq_{x}", x), index=options.index(existing_config['frequency']) if existing_config else 0)
                            hour = st.number_input(L['label_hour'], 0, 23, value=existing_config['hour'] if existing_config else 8)
                            recipients = st.text_input(L['label_recipients'], value=", ".join(existing_config['email_recipients']) if existing_config else "")
                            c_f1, c_f2 = st.columns(2)
                            with c_f1:
                                if st.form_submit_button(L['btn_save_config'], use_container_width=True):
                                    payload = {"monitoring_set_id": selected_set_id, "frequency": freq, "hour": hour, "email_recipients": [r.strip() for r in recipients.split(",") if r.strip()]}
                                    if requests.post(f"{API_BASE_URL}/reports/config", json=payload, params={"user_id": user['id']}).status_code == 200:
                                        st.success(L['msg_saved']); st.session_state.report_edit_mode = False; st.rerun()
                            with c_f2:
                                if st.session_state.report_edit_mode:
                                    if st.form_submit_button(L['btn_cancel'], use_container_width=True):
                                        st.session_state.report_edit_mode = False; st.rerun()
                    st.divider(); st.subheader("Histórico de Relatórios")
                    hist_res = requests.get(f"{API_BASE_URL}/reports/history/{selected_set_id}")
                    if hist_res.status_code == 200:
                        history = hist_res.json()
                        if history:
                            df_hist = pd.DataFrame(history)
                            for col in ['generated_at', 'period_start', 'period_end']: df_hist[col] = pd.to_datetime(df_hist[col]).dt.strftime('%Y-%m-%d %H:%M')
                            df_hist = df_hist[['generated_at', 'period_start', 'period_end', 'file_url']]
                            df_hist.columns = [L['th_date'], 'Início', 'Fim', 'Link']; st.dataframe(df_hist, use_container_width=True)
                        else: st.info("Nenhum relatório gerado ainda.")
                else: st.warning(L['msg_no_sets'])
        except Exception as e: st.error(f"Erro: {e}")
    with tab2:
        st.subheader(L['header_billing'])
        try:
            inv_res = requests.get(f"{API_BASE_URL}/invoices", params={"user_id": user['id']})
            if inv_res.status_code == 200:
                invoices = inv_res.json()
                if invoices:
                    for inv in invoices:
                        with st.container(border=True):
                            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                            c1.write(f"**Período:** {inv['billing_period']}"); c2.write(f"**{L['th_amount']}:** R$ {inv['amount']/100:.2f}")
                            c3.write(f"**{L['th_due']}:** {inv['due_date']}"); status_color = "green" if inv['status'] == "paid" else "red"
                            c4.markdown(f"<span style='color: {status_color}; font-weight: bold;'>{inv['status'].upper()}</span>", unsafe_allow_html=True)
                            if inv['pdf_url']: st.link_button("Download PDF", inv['pdf_url'], size="small")
                else: st.info("Nenhuma fatura encontrada.")
        except Exception as e: st.error(f"Erro ao carregar faturas: {e}")
    with tab3:
        st.header(L['header_reports'])
        try:
            response = requests.get(f"{API_BASE_URL}/mentions", params={"limit": 50})
            if response.status_code == 200:
                mentions = response.json()
                if not mentions: st.info(L['msg_no_mentions'])
                else:
                    for m in mentions:
                        with st.container(border=True):
                            col_m1, col_m2 = st.columns([3, 1])
                            with col_m1:
                                st.subheader(f"{m['program_name']}"); st.write(f"**{L['th_channel']}:** {m['channel']}")
                                occ_time = pd.to_datetime(m['occurrence_time']).strftime('%Y-%m-%d %H:%M'); st.write(f"🕒 {occ_time}")
                            with col_m2:
                                if m['video_url']: st.link_button("Clipe", m['video_url'], use_container_width=True)
                            st.info(f"💬 {m['transcription']}")
                            if m['context']: st.caption(f"Contexto: {m['context']}")
        except Exception as e: st.error(f"{L['msg_connection_error']} {e}")
elif user['role'] == "client" and page == L['nav_test']:
    st.header(L['header_test'])
    email_dest = st.text_input("Email", value=user['email'])
    if st.button("Send Test"):
        with st.spinner("Sending..."):
            try:
                res = email_service.send_notification(to=email_dest, subject="Test", text="Mentions On-Demand Test")
                st.success("Sent!")
            except Exception as e: st.error(str(e))
