import streamlit as st
import pandas as pd
import uuid
import requests
import os
import sys
from datetime import time, datetime, timedelta

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.services.email_service import email_service

API_BASE_URL = "http://localhost:8000/api"

def refresh_user():
    if st.session_state.get('logged_in') and st.session_state.get('user'):
        try:
            res = requests.get(f"{API_BASE_URL}/user/{st.session_state.user['id']}")
            if res.status_code == 200:
                st.session_state.user = res.json()
        except:
            pass

def format_days(days_list, lang):
    if not days_list:
        return ""
    if lang == "PT":
        day_names = {1: "Seg", 2: "Ter", 3: "Qua", 4: "Qui", 5: "Sex", 6: "Sáb", 7: "Dom"}
    elif lang == "ES":
        day_names = {1: "Lun", 2: "Mar", 3: "Mié", 4: "Jue", 5: "Vie", 6: "Sáb", 7: "Dom"}
    else:
        day_names = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
    return ", ".join([day_names[d] for d in sorted(days_list)])

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
if 'lang' not in st.session_state: st.session_state.lang = "PT"
if 'edit_id' not in st.session_state: st.session_state.edit_id = None
if 'temp_terms' not in st.session_state: st.session_state.temp_terms = []

# Restore session from query parameters (survives page refresh/language switch)
if not st.session_state.logged_in and "user_id" in st.query_params:
    try:
        q_user_id = st.query_params["user_id"]
        if isinstance(q_user_id, list): q_user_id = q_user_id[0]
        res = requests.get(f"{API_BASE_URL}/user/{q_user_id}")
        if res.status_code == 200:
            st.session_state.user = res.json()
            st.session_state.logged_in = True
            if st.session_state.user.get('status') == "pending_approval":
                st.session_state.client_nav_page = "docs"
            else:
                st.session_state.client_nav_page = "list"
    except:
        pass
if 'temp_rules' not in st.session_state: st.session_state.temp_rules = []
if 'set_name' not in st.session_state: st.session_state.set_name = ""
if 'report_edit_mode' not in st.session_state: st.session_state.report_edit_mode = False
if 'show_form' not in st.session_state: st.session_state.show_form = False
if 'show_register' not in st.session_state: st.session_state.show_register = False

# --- LANGUAGE PARAMETER HANDLING ---
if "lang" in st.query_params:
    new_lang = st.query_params["lang"]
    if isinstance(new_lang, list): new_lang = new_lang[0]
    if new_lang in ["PT", "GB", "ES"] and new_lang != st.session_state.get("lang"):
        st.session_state.lang = new_lang
        st.rerun()

# --- CSS INJECTION (ADINSIGHTS STYLE) ---
st.markdown("""
    <style>
    :root {
        --color-primary: #000000;
        --color-secondary: #0F21FD;
        --color-third: #001E78;
        --surface-secondary: #F5F5F7;
        --font-main: 'Geist', 'Inter', 'Verdana', sans-serif;
    }

    .stApp {
        background-color: var(--surface-secondary);
        font-family: var(--font-main);
    }

    /* Force Gray Buttons */
    div.stButton > button {
        background-color: #64748b !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }

    div.stButton > button:hover {
        background-color: #475569 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FAFAFA !important;
        border-right: 1px solid #E8E8EE;
    }

    section[data-testid="stSidebar"] .stRadio label p {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #0F21FD !important;
    }

    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        color: #000000 !important;
        margin-bottom: 15px !important;
    }

    /* Header Component */
    .header-container {
        text-align: center;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px 0;
    }

    .kantar-logo-header {
        background-image: url("data:image/svg+xml,%3Csvg width='70' height='40' viewBox='0 0 70 40' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M66.0818 2H3V37.8857H66.0818V2Z' fill='%230F21FD'/%3E%3Cpath d='M9.96373 12.4643H7.16479V25.6554H9.96373V12.4643Z' fill='white'/%3E%3Cpath d='M15.2346 23.3519H18.0167C18.6924 23.3519 19.2358 23.2132 19.647 22.9335C20.0582 22.6538 20.2649 22.2378 20.2649 21.6784C20.2649 21.1213 20.0582 20.6957 19.647 20.4062C19.2358 20.1143 18.6924 19.9684 18.0167 19.9684H15.2346V23.3519ZM15.2346 17.9251H17.4444C18.1321 17.9251 18.6827 17.7889 19.0939 17.5165C19.5051 17.244 19.7119 16.8549 19.7119 16.3465C19.7119 15.8016 19.5123 15.4027 19.1132 15.1473C18.714 14.8943 18.1585 14.7678 17.4468 14.7678H15.237V17.9251H15.2346ZM12.4356 25.6554V12.4643H17.5213C19.142 12.4643 20.3828 12.7513 21.2436 13.3278C22.102 13.9043 22.5325 14.8116 22.5325 16.0497C22.5325 16.5946 22.4219 17.0689 22.2006 17.4703C21.9794 17.874 21.6572 18.1927 21.234 18.4262C20.8108 18.6622 20.2962 18.8032 19.6951 18.8543V18.8178C20.7891 18.8932 21.6259 19.2119 22.2103 19.7738C22.7922 20.3381 23.0855 21.0824 23.0855 22.0116C23.0855 23.2376 22.6575 24.1522 21.8063 24.7505C20.9527 25.3513 19.7335 25.6505 18.1489 25.6505H12.438L12.4356 25.6554Z' fill='white'/%3E%3Cpath d='M30.9677 23.5732C31.7035 23.5732 32.3335 23.3981 32.8553 23.043C33.3771 22.6903 33.7763 22.1795 34.0528 21.5105C34.3293 20.8416 34.4664 20.0316 34.4664 19.0781C34.4664 18.1246 34.3293 17.3097 34.0528 16.6359C33.7763 15.9622 33.3771 15.444 32.8553 15.084C32.3335 14.724 31.7035 14.544 30.9677 14.544C30.2319 14.544 29.6236 14.724 29.1066 15.084C28.592 15.444 28.1953 15.9597 27.9187 16.6359C27.6422 17.3122 27.5051 18.1246 27.5051 19.0781C27.5051 20.0316 27.6422 20.844 27.9187 21.5105C28.1953 22.1795 28.5944 22.6903 29.1162 23.043C29.638 23.3957 30.256 23.5732 30.9677 23.5732ZM30.987 25.9522C29.6596 25.9522 28.5223 25.6724 27.5701 25.1154C26.6178 24.5584 25.8869 23.7654 25.3771 22.7365C24.8673 21.7076 24.6124 20.4889 24.6124 19.0757C24.6124 17.6624 24.8673 16.4413 25.3771 15.4076C25.8869 14.3738 26.6178 13.5735 27.5701 13.0116C28.5223 12.4473 29.662 12.1651 30.987 12.1651C32.3263 12.1651 33.4685 12.4473 34.4135 13.0116C35.3585 13.5759 36.0871 14.3738 36.5969 15.4076C37.1066 16.4413 37.3615 17.6649 37.3615 19.0757C37.3615 20.4885 37.1066 21.7076 36.5969 22.7365C36.0871 23.7654 35.3561 24.5559 34.4039 25.1154C33.4517 25.6724 32.3119 25.9522 30.987 25.9522Z' fill='white'/%3E%3Cpath d='M42.0024 18.7254H44.2675C45.0033 18.7254 45.5756 18.5624 45.9795 18.2341C46.3859 17.9057 46.5879 17.4192 46.5879 16.7746C46.5879 16.1422 46.3883 15.663 45.9891 15.3346C45.59 15.0062 45.0153 14.8432 44.2675 14.8432H42.0024V18.7254ZM39.2034 25.6554V12.4643H44.4358C46.0084 12.4643 47.2395 12.8486 48.1292 13.6173C49.0189 14.3859 49.4638 15.4368 49.4638 16.7746C49.4638 17.6551 49.2642 18.4189 48.865 19.0684C48.4659 19.7178 47.8888 20.2213 47.1337 20.5740C46.3787 20.9268 45.4794 21.1043 44.4358 21.1043H42.0048V25.6554H39.2034Z' fill='white'/%3E%3Cpath d='M51.2143 25.6554V12.4643H60.3156V14.8408H54.0156V17.8692H60.0944V20.2116H54.0156V23.2765H60.4623V25.6554H51.2143Z' fill='white'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        width: 105px;
        height: 60px;
        display: block;
        background-size: contain;
        margin: 0 auto 10px auto;
    }

    .flag-group {
        display: flex;
        gap: 15px;
        justify-content: center;
        margin-bottom: 15px;
    }

    .flag-item {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        border: 2px solid #E8E8EE;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: transform 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: white;
    }

    .flag-item:hover {
        transform: scale(1.1);
        border-color: #0F21FD;
    }

    .flag-item svg {
        width: 35px;
        height: 35px;
    }

    /* Inputs */
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
        background-color: #F4F4F4 !important;
        border: 1px solid #D9D9D9 !important;
        border-radius: 4px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- I18N DICTIONARY ---
LANG_DATA = {
    "GB": {
        "title": "Mentions On-Demand",
        "nav_new": "Schedule",
        "nav_list": "Monitoring",
        "nav_reports": "Reports",
        "nav_billing": "Billing & Invoices",
        "nav_test": "Test Email",
        "header_new": "New Monitoring Set",
        "header_list": "My Monitoring Sets",
        "header_reports": "Reports & Configuration",
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
        "nav_profile": "My Profile",
        "op_nav_approvals": "Pending Approvals",
        "op_nav_health": "System Health",
        "op_nav_clients": "Customer Management",
        "adm_nav_logs": "Audit Logs",
        "adm_nav_config": "Global Config",
        "adm_nav_users": "User Management",
        "lbl_active_sets": "Active Sets",
        "lbl_total_min": "Total Min/Week",
        "op_nav_title": "Operator",
        "adm_nav_title": "Administrator",
        "btn_reprocess": "Reprocess",
        "btn_block": "Block",
        "btn_unblock": "Unblock",
        "btn_adjust_credit": "Adjust Limit",
        "login_header": "Sign In",
        "login_btn": "Access System",
        "login_new_here": "New here? Register",
        "reg_header": "New Registration",
        "reg_company": "Trading Name",
        "reg_contact_name": "Contact Name",
        "reg_btn_finish": "Finish Registration",
        "reg_msg_success": "Registration completed successfully!",
        "reg_msg_pending": "Your account is awaiting approval by the operator. You will receive a notification once you can access it.",
        "reg_btn_back": "Back to Login",
        "msg_fill_all": "Please fill in all fields.",
        "msg_login_error": "Incorrect email or password.",
        "tab_new_clients": "New Clients",
        "tab_monitoring": "Monitoring",
        "msg_no_pending_clients": "No new clients awaiting approval.",
        "msg_no_pending_sets": "No monitoring sets awaiting approval.",
        "lbl_docs_sent": "📁 Documents Sent",
        "lbl_docs_verified": "✅ Docs Verified",
        "lbl_docs_missing": "❌ Missing Documents",
        "btn_view_approve": "View Details / Approve",
        "lbl_limit_exceeded": "⚠️ Limit Exceeded",
        "lbl_justification": "Approval justification",
        "btn_approve_exception": "Approve with Exception",
        "btn_approve_set": "Approve Set",
        "nav_docs": "Docs & Contracts",
        "header_docs": "Documentation & Contracts",
        "lbl_upload_docs": "Upload Documents",
        "lbl_select_file": "Select file",
        "btn_send_docs": "Send Documents",
        "msg_docs_success": "Documents sent successfully!",
        "lbl_certidao": "Tax Clearance / CNPJ Proof",
        "lbl_contrato": "Social Contract",
        "lbl_commercial_team": "Commercial Team",
        "lbl_report_config": "Automatic Report Configuration",
        "lbl_select_set": "Select Set to Configure",
        "lbl_include_audience": "Include Audience Data (Premium)",
        "lbl_context_seconds": "Context Seconds (Clip)",
        "placeholder_set_name": "Ex: Competitor Clipping",
        "placeholder_term": "Type and click +",
        "placeholder_program": "Search for program name...",
        "msg_error_channels": "Error loading channels.",
        "msg_no_programs": "No programs found.",
        "header_rules_selected": "Rules Selected",
        "btn_add": "Add",
        "lbl_tagline": "AI TV Monitoring System",
        "lbl_email": "Email",
        "lbl_password": "Password",
        "lbl_razao_social": "Corporate Name",
        "lbl_cnpj": "CNPJ",
        "lbl_address": "Address",
        "lbl_phone": "Phone"
    },
    "PT": {
        "title": "Mentions On-Demand",
        "nav_new": "Novo Agendamento",
        "nav_list": "Meus Conjuntos",
        "nav_reports": "Relatórios",
        "nav_billing": "Faturamento & Faturas",
        "nav_test": "Teste de Email",
        "header_new": "Novo Conjunto de Monitoramento",
        "header_list": "Meus Conjuntos de Monitoramento",
        "header_reports": "Configuração de Relatórios",
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
        "msg_no_sets": "Nenhum conjunto de monitoramento encontrado.",
        "msg_no_mentions": "Nenhuma ocorrência encontrada para este conjunto.",
        "msg_connection_error": "Erro de conexão:",
        "th_channel": "Canal",
        "th_program": "Programa",
        "th_time": "Janela Horária",
        "th_days": "Dias",
        "th_actions": "Ações",
        "freq_daily": "Diário",
        "freq_weekly": "Semanal",
        "freq_monthly": "Mensal",
        "btn_edit_config": "Editar Configuração",
        "btn_cancel": "Cancelar",
        "tab_occurrences": "Ocorrências",
        "btn_logout": "Sair",
        "btn_new_set": "+ Novo Monitoramento",
        "btn_back": "Voltar para Lista",
        "nav_profile": "Meu Perfil",
        "op_nav_approvals": "Aprovações Pendentes",
        "op_nav_health": "Saúde do Sistema",
        "op_nav_clients": "Gestão de Clientes",
        "adm_nav_logs": "Logs de Auditoria",
        "adm_nav_config": "Configuração Global",
        "adm_nav_users": "Gestão de Usuários",
        "lbl_active_sets": "Sets Ativos",
        "lbl_total_min": "Total Min/Semana",
        "op_nav_title": "Operador",
        "adm_nav_title": "Administrador",
        "btn_reprocess": "Reprocessar",
        "btn_block": "Bloquear",
        "btn_unblock": "Desbloquear",
        "btn_adjust_credit": "Ajustar Limite",
        "login_header": "Entrar",
        "login_btn": "Acessar Sistema",
        "login_new_here": "Novo por aqui? Cadastre-se",
        "reg_header": "Novo Cadastro",
        "reg_company": "Nome Fantasia",
        "reg_contact_name": "Nome do Contato",
        "reg_btn_finish": "Finalizar Cadastro",
        "reg_msg_success": "Cadastro realizado com sucesso!",
        "reg_msg_pending": "Sua conta aguarda aprovação do operador. Você receberá uma notificação assim que puder acessar.",
        "reg_btn_back": "Voltar ao Login",
        "msg_fill_all": "Por favor preencha todos os campos.",
        "msg_login_error": "E-mail ou senha incorretos.",
        "tab_new_clients": "Novos Clientes",
        "tab_monitoring": "Monitoramentos",
        "msg_no_pending_clients": "Nenhum novo cliente aguardando aprovação.",
        "msg_no_pending_sets": "Nenhum conjunto de monitoramento aguardando aprovação.",
        "lbl_docs_sent": "📁 Documentos Enviados",
        "lbl_docs_verified": "✅ Docs Verificados",
        "lbl_docs_missing": "❌ Faltando Documentos",
        "btn_view_approve": "Ver Detalhes / Aprovar",
        "lbl_limit_exceeded": "⚠️ Limite Excedido",
        "lbl_justification": "Justificativa da aprovação",
        "btn_approve_exception": "Aprovar com Exceção",
        "btn_approve_set": "Aprovar Set",
        "nav_docs": "Docs & Contratos",
        "header_docs": "Documentação & Contratos",
        "lbl_upload_docs": "Upload de Documentos",
        "lbl_select_file": "Selecione o arquivo",
        "btn_send_docs": "Enviar Documentos",
        "msg_docs_success": "Documentos enviados com sucesso!",
        "lbl_certidao": "Certidão de Quitação / Comprovante CNPJ",
        "lbl_contrato": "Contrato Social",
        "lbl_commercial_team": "Time Comercial",
        "lbl_report_config": "Configuração de Relatório Automático",
        "lbl_select_set": "Selecione o Conjunto para Configurar",
        "lbl_include_audience": "Incluir Dados de Audiência (Premium)",
        "lbl_context_seconds": "Segundos de Contexto (Clip)",
        "placeholder_set_name": "Ex: Clipping de Concorrência",
        "placeholder_term": "Digite e clique em +",
        "placeholder_program": "Busque o nome do programa...",
        "msg_error_channels": "Erro ao carregar canais.",
        "msg_no_programs": "Nenhum programa encontrado.",
        "header_rules_selected": "Regras Selecionadas",
        "btn_add": "Adicionar",
        "lbl_tagline": "Sistema IA de Monitoramento de TV",
        "lbl_email": "E-mail",
        "lbl_password": "Senha",
        "lbl_razao_social": "Razão Social",
        "lbl_cnpj": "CNPJ",
        "lbl_address": "Endereço",
        "lbl_phone": "Telefone"
    },
    "ES": {
        "title": "Mentions On-Demand",
        "nav_new": "Nuevo Programación",
        "nav_list": "Mis Conjuntos",
        "nav_reports": "Informes",
        "nav_billing": "Facturación y Facturas",
        "nav_test": "Prueba de Email",
        "header_new": "Nuevo Conjunto de Monitoreo",
        "header_list": "Mis Conjuntos de Monitoreo",
        "header_reports": "Informes y Configuración",
        "header_billing": "Historial de Facturación",
        "label_frequency": "Frecuencia del Informe",
        "label_hour": "Horario Preferencial",
        "label_recipients": "Destinatarios (separados por coma)",
        "btn_save_config": "Guardar Configuración",
        "th_date": "Fecha de Generación",
        "th_period": "Periodo",
        "th_amount": "Valor",
        "th_due": "Vencimiento",
        "th_status": "Status",
        "header_test": "Prueba de Envío (AgentMail)",
        "label_name": "Nombre del Monitoreo",
        "label_terms": "Términos de Búsqueda (Tags)",
        "label_channel": "Seleccione el Canal",
        "label_program": "Buscar Programa en la Grilla",
        "btn_add_term": "+ Añadir Término",
        "btn_add_rule": "Consultar Grilla de Programación",
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
        "msg_no_sets": "No se encontraron conjuntos de monitoreo.",
        "msg_no_mentions": "No se encontraron ocurrencias para este conjunto.",
        "msg_connection_error": "Error de conexión:",
        "th_channel": "Canal",
        "th_program": "Programa",
        "th_time": "Ventana Horaria",
        "th_days": "Días",
        "th_actions": "Acciones",
        "freq_daily": "Diario",
        "freq_weekly": "Semanal",
        "freq_monthly": "Mensual",
        "btn_edit_config": "Editar Configuración",
        "btn_cancel": "Cancelar",
        "tab_occurrences": "Ocurrencias",
        "btn_logout": "Salir",
        "btn_new_set": "+ Nuevo Monitoreo",
        "btn_back": "Volver a la Lista",
        "nav_profile": "Mi Perfil",
        "op_nav_approvals": "Aprobaciones Pendientes",
        "op_nav_health": "Salud del Sistema",
        "op_nav_clients": "Gestão de Clientes",
        "adm_nav_logs": "Logs de Auditoría",
        "adm_nav_config": "Configuração Global",
        "adm_nav_users": "Gestão de Usuários",
        "lbl_active_sets": "Sets Activos",
        "lbl_total_min": "Total Min/Semana",
        "op_nav_title": "Operador",
        "adm_nav_title": "Administrador",
        "btn_reprocess": "Reprocesar",
        "btn_block": "Bloquear",
        "btn_unblock": "Desbloquear",
        "btn_adjust_credit": "Ajustar Límite",
        "login_header": "Entrar",
        "login_btn": "Acceder al Sistema",
        "login_new_here": "¿Es nuevo aquí? Regístrese",
        "reg_header": "Nuevo Registro",
        "reg_company": "Nombre de Fantasía",
        "reg_contact_name": "Nombre del Contacto",
        "reg_btn_finish": "Finalizar Registro",
        "reg_msg_success": "¡Registro completado con éxito!",
        "reg_msg_pending": "Su cuenta está esperando la aprobación del operador. Recibirá una notificación tan pronto como pueda acceder.",
        "reg_btn_back": "Volver al Login",
        "msg_fill_all": "Por favor complete todos los campos.",
        "msg_login_error": "Correo electrónico o contraseña incorrectos.",
        "tab_new_clients": "Nuevos Clientes",
        "tab_monitoring": "Monitoreos",
        "msg_no_pending_clients": "No hay nuevos clientes pendientes de aprobación.",
        "msg_no_pending_sets": "No hay conjuntos de monitoreo pendientes de aprobación.",
        "lbl_docs_sent": "📁 Documentos Enviados",
        "lbl_docs_verified": "✅ Docs Verificados",
        "lbl_docs_missing": "❌ Sin Documentos",
        "btn_view_approve": "Ver Detalles / Aprobar",
        "lbl_limit_exceeded": "⚠️ Límite Excedido",
        "lbl_justification": "Justificación de la aprobación",
        "btn_approve_exception": "Aprobar con Excepción",
        "btn_approve_set": "Aprobar Set",
        "nav_docs": "Docs y Contratos",
        "header_docs": "Documentación y Contratos",
        "lbl_upload_docs": "Carga de Documentos",
        "lbl_select_file": "Seleccione el archivo",
        "btn_send_docs": "Enviar Documentos",
        "msg_docs_success": "¡Documentos enviados con éxito!",
        "lbl_certidao": "Certificado de Situación Fiscal (CNPJ)",
        "lbl_contrato": "Contrato Social",
        "lbl_commercial_team": "Equipo Comercial",
        "lbl_report_config": "Configuración de Informes Automáticos",
        "lbl_select_set": "Seleccione el Conjunto para Configurar",
        "lbl_include_audience": "Incluir Datos de Audiencia (Premium)",
        "lbl_context_seconds": "Segundos de Contexto (Clip)",
        "placeholder_set_name": "Ej: Clipping de Competencia",
        "placeholder_term": "Escriba y haga clic en +",
        "placeholder_program": "Escriba el nombre del programa...",
        "msg_error_channels": "Error al cargar canales.",
        "msg_no_programs": "No se encontraron programas.",
        "header_rules_selected": "Reglas Seleccionadas",
        "btn_add": "Añadir",
        "lbl_tagline": "Sistema IA de Monitoreo de TV",
        "lbl_email": "Correo electrónico",
        "lbl_password": "Contraseña",
        "lbl_razao_social": "Razón Social",
        "lbl_cnpj": "CNPJ",
        "lbl_address": "Dirección",
        "lbl_phone": "Teléfono"
    }
}

# --- SHARED FUNCTIONS ---

# Hybrid Language Selector
def render_lang_selector(sidebar=True, return_html=False):
    # SVG Definitions
    svg_br = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="#43a047" d="M0 0h512v512H0z"/><path fill="#ffeb3b" d="M256 50.3L50.3 256l205.7 205.7L461.7 256 256 50.3z"/><circle cx="256" cy="256" r="95" fill="#3949ab"/></svg>'
    svg_en = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="#012169" d="M0 0h512v512H0z"/><path stroke="white" stroke-width="64" d="M0 0l512 512M512 0L0 512"/><path stroke="#c8102e" stroke-width="40" d="M0 0l512 512M512 0L0 512"/><path stroke="white" stroke-width="104" d="M256 0v512M0 256h512"/><path stroke="#c8102e" stroke-width="64" d="M256 0v512M0 256h512"/></svg>'
    svg_es = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="#aa151b" d="M0 0h512v512H0z"/><path fill="#f1bf00" d="M0 128h512v256H0z"/></svg>'

    user_param = ""
    if st.session_state.get("logged_in") and st.session_state.get("user"):
        user_param = f"&user_id={st.session_state.user['id']}"

    html = f"""
<div class="flag-group">
<a href="?lang=PT{user_param}" target="_self" style="text-decoration: none;">
<div class="flag-item" title="Português">{svg_br}</div>
</a>
<a href="?lang=GB{user_param}" target="_self" style="text-decoration: none;">
<div class="flag-item" title="English">{svg_en}</div>
</a>
<a href="?lang=ES{user_param}" target="_self" style="text-decoration: none;">
<div class="flag-item" title="Español">{svg_es}</div>
</a>
</div>
"""
    
    if return_html:
        return html

    container = st.sidebar if sidebar else st.container()
    with container:
        if sidebar: st.write("---")
        st.markdown(html, unsafe_allow_html=True)
        if sidebar: st.write("---")

L = LANG_DATA.get(st.session_state.lang, LANG_DATA["PT"])

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
            set_name = st.text_input(L['label_name'], value=st.session_state.set_name, placeholder=L['placeholder_set_name'])
            st.session_state.set_name = set_name
            
            st.write("---")
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                if 'audience_enabled' not in st.session_state: st.session_state.audience_enabled = False
                audience_enabled = st.checkbox(L['lbl_include_audience'], value=st.session_state.audience_enabled)
                st.session_state.audience_enabled = audience_enabled
            with col_opt2:
                if 'context_secs' not in st.session_state: st.session_state.context_secs = 15
                context_secs = st.number_input(L['lbl_context_seconds'], 5, 60, st.session_state.context_secs)
                st.session_state.context_secs = context_secs
        with col2:
            if 'term_input' not in st.session_state: st.session_state.term_input = ""
            
            def add_term():
                term = st.session_state.term_input
                if term and term not in st.session_state.temp_terms:
                    st.session_state.temp_terms.append(term)
                    st.session_state.term_input = "" # Clear input

            st.text_input(L['label_terms'], key="term_input", placeholder=L['placeholder_term'], on_change=add_term)
            if st.button(L['btn_add_term']):
                add_term()
                st.rerun()
            
            if st.session_state.temp_terms:
                st.write("Tags:", " ".join([f"`{t}`" for t in st.session_state.temp_terms]))

    st.subheader(L['btn_add_rule'])
    
    try:
        ch_res = requests.get(f"{API_BASE_URL}/grid/channels")
        channels = ch_res.json() if ch_res.status_code == 200 else []
    except:
        channels = []
        
    selected_channel = st.selectbox(L['label_channel'], [""] + channels)
    
    if selected_channel:
        try:
            params = {"channel": selected_channel, "limit": 100}
            response = requests.get(f"{API_BASE_URL}/grid/lookup", params=params)
            if response.status_code == 200:
                results = response.json().get("items", [])
                if results:
                    # Group by program name to extract start/end times and days of occurrence
                    programs_map = {}
                    for res in results:
                        p_name = res["program_name"]
                        s_time = res["start_time"]
                        e_time = res["end_time"]
                        b_date_str = res["broadcast_date"]
                        b_date = datetime.strptime(b_date_str, "%Y-%m-%d").date()
                        day_num = b_date.weekday() + 1 # Monday=1, Sunday=7
                        
                        if p_name not in programs_map:
                            programs_map[p_name] = {
                                "start_time": s_time,
                                "end_time": e_time,
                                "days_of_week": {day_num}
                            }
                        else:
                            programs_map[p_name]["days_of_week"].add(day_num)
                    
                    # Dropdown for Program Name
                    sorted_programs = sorted(list(programs_map.keys()))
                    selected_program_label = "Escolha o Programa" if st.session_state.lang == "PT" else ("Select Program" if st.session_state.lang == "EN" else "Seleccione el Programa")
                    selected_program = st.selectbox(selected_program_label, [""] + sorted_programs)
                    
                    if selected_program:
                        prog_info = programs_map[selected_program]
                        
                        # Format times to HH:MM for cleaner display
                        try:
                            s_dt = datetime.strptime(prog_info["start_time"], "%H:%M:%S")
                            s_formatted = s_dt.strftime("%H:%M")
                        except:
                            s_formatted = prog_info["start_time"]
                            
                        try:
                            e_dt = datetime.strptime(prog_info["end_time"], "%H:%M:%S")
                            e_formatted = e_dt.strftime("%H:%M")
                        except:
                            e_formatted = prog_info["end_time"]
                            
                        st.info(f"**{selected_program}** | {s_formatted} - {e_formatted}")
                        
                        # Days of the week checkboxes
                        if st.session_state.lang == "PT":
                            days_info = [("Seg", 1), ("Ter", 2), ("Qua", 3), ("Qui", 4), ("Sex", 5), ("Sáb", 6), ("Dom", 7)]
                            label_days = "Habilitar Dias da Semana"
                            btn_add_lbl = "+ Adicionar Programa ao Monitoramento"
                        elif st.session_state.lang == "ES":
                            days_info = [("Lun", 1), ("Mar", 2), ("Mié", 3), ("Jue", 4), ("Vie", 5), ("Sáb", 6), ("Dom", 7)]
                            label_days = "Habilitar Días de la Semana"
                            btn_add_lbl = "+ Agregar Programa al Monitoreo"
                        else:
                            days_info = [("Mon", 1), ("Tue", 2), ("Wed", 3), ("Thu", 4), ("Fri", 5), ("Sat", 6), ("Sun", 7)]
                            label_days = "Enable Days of the Week"
                            btn_add_lbl = "+ Add Program to Monitoring"
                            
                        st.write(f"**{label_days}**")
                        day_cols = st.columns(7)
                        selected_days = []
                        for idx, (day_name, day_num) in enumerate(days_info):
                            with day_cols[idx]:
                                is_prechecked = day_num in prog_info["days_of_week"]
                                checked = st.checkbox(day_name, value=is_prechecked, key=f"day_chk_{day_num}_{selected_program}")
                                if checked:
                                    selected_days.append(day_num)
                                    
                        if st.button(btn_add_lbl, type="primary", use_container_width=True):
                            if not selected_days:
                                st.error("Selecione pelo menos um dia da semana!" if st.session_state.lang == "PT" else ("Please select at least one day of the week!" if st.session_state.lang == "EN" else "¡Seleccione al menos un día de la semana!"))
                            else:
                                new_rule = {
                                    "channel": selected_channel,
                                    "program_name": selected_program,
                                    "start_time": prog_info["start_time"],
                                    "end_time": prog_info["end_time"],
                                    "days_of_week": selected_days
                                }
                                st.session_state.temp_rules.append(new_rule)
                                st.success(f"**{selected_program}** adicionado!" if st.session_state.lang == "PT" else f"**{selected_program}** added!" if st.session_state.lang == "EN" else f"¡**{selected_program}** agregado!")
                                st.rerun()
                else:
                    st.warning(L['msg_no_programs'])
        except Exception as e:
            st.error(f"{L['msg_connection_error']} {e}")

    if st.session_state.temp_rules:
        st.write(f"### {L['header_rules_selected']}")
        for i, r in enumerate(st.session_state.temp_rules):
            col_r1, col_r2 = st.columns([4, 1])
            with col_r1:
                st.write(f"**{r['channel']}**: {r['program_name']} ({r['start_time']}-{r['end_time']}) | *{format_days(r['days_of_week'], st.session_state.lang)}*")
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
    # Use Markdown for flags and logo together
    lang_html = render_lang_selector(sidebar=False, return_html=True)
    
    st.markdown(f"""
<div class="header-container">
{lang_html}
<div style="width: 140px; margin: 0 auto 10px auto;">
<div class="kantar-logo-header"></div>
</div>
<h1 style='color: #0F21FD; margin: 0; font-weight: 400; font-size: 28px; text-align: center;'>{L['title']}</h1>
<p style='color: #64748b; font-size: 14px; margin-bottom: 20px; text-align: center;'>{L['lbl_tagline']}</p>
</div>
""", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        if not st.session_state.show_register:
            with st.container(border=True):
                st.subheader(L['login_header'])
                email = st.text_input(L['lbl_email'], placeholder="contato@pixelwave.com")
                password = st.text_input(L['lbl_password'], type="password", placeholder="****")
                submit = st.button(L['login_btn'], use_container_width=True, type="primary")
                
                if submit:
                    if not email or not password:
                        st.warning(L['msg_fill_all'])
                    else:
                        try:
                            res = requests.post(f"{API_BASE_URL}/auth/login", json={"email": email, "password": password})
                            if res.status_code == 200:
                                st.session_state.user = res.json()
                                st.session_state.logged_in = True
                                if st.session_state.user.get('status') == "pending_approval":
                                    st.session_state.client_nav_page = "docs"
                                else:
                                    st.session_state.client_nav_page = "list"
                                st.session_state.show_form = False
                                st.rerun()
                            elif res.status_code == 403:
                                st.warning(res.json().get("detail", "Acesso restrito."))
                            else:
                                st.error(L['msg_login_error'])
                        except Exception as e:
                            st.error(f"{L['msg_connection_error']} {e}")
                
                st.write("---")
                if st.button(L['login_new_here'], use_container_width=True):
                    st.session_state.show_register = True
                    st.session_state.reg_success = False
                    st.rerun()
        else:
            with st.container(border=True):
                if st.session_state.reg_success:
                    st.success(L['reg_msg_success'])
                    st.info(L['reg_msg_pending'])
                    if st.button(L['reg_btn_back'], use_container_width=True):
                        st.session_state.show_register = False
                        st.session_state.reg_success = False
                        st.rerun()
                else:
                    st.subheader(L['reg_header'])
                    with st.form("public_register_form"):
                        reg_company = st.text_input(L['reg_company'], placeholder="Sua Agência")
                        reg_razao = st.text_input(L['lbl_razao_social'])
                        reg_cnpj = st.text_input(L['lbl_cnpj'])
                        reg_name = st.text_input(L['reg_contact_name'])
                        reg_email = st.text_input(L['lbl_email'])
                        reg_pass = st.text_input(L['lbl_password'], type="password")
                        reg_phone = st.text_input(L['lbl_phone'])
                        reg_address = st.text_area(L['lbl_address'])
                        
                        st.caption(L['reg_msg_pending'])
                        
                        col_reg1, col_reg2 = st.columns(2)
                        with col_reg1:
                            reg_submit = st.form_submit_button(L['reg_btn_finish'], type="primary", use_container_width=True)
                        with col_reg2:
                            if st.form_submit_button(L['btn_cancel'], use_container_width=True):
                                st.session_state.show_register = False
                                st.rerun()
                        
                        if reg_submit:
                            if not reg_email or not reg_pass or not reg_company:
                                st.error(L['msg_fill_all'])
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
                                    st.error(f"{L['msg_connection_error']} {e}")
            
            if not st.session_state.reg_success:
                if st.button(L['btn_back'], key="back_from_reg"):
                    st.session_state.show_register = False
                    st.rerun()

        st.markdown(f"<br><small style='color: #94a3b8; display: block; text-align: center;'>Versão 1.3.4 - {L['lbl_commercial_team']}</small>", unsafe_allow_html=True)
    st.stop()

# --- HEADER (LOGGED IN) ---
user = st.session_state.user

st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #E8E8EE; padding-bottom: 15px; margin-bottom: 25px;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div class="kantar-logo-header" style="margin:0; width: 80px; height: 45px;"></div>
            <h1 style="margin: 0; color: #0F21FD; font-size: 24px; font-weight: 500;">{L['title']}</h1>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.markdown(f"""
    <div style='background-color: #F5F5F7; padding: 15px; border-radius: 10px; border: 1px solid #E8E8EE; margin-bottom: 20px;'>
        <div style='font-size: 0.8rem; color: #64748b; text-transform: uppercase; font-weight: 700;'>{L['nav_profile']}</div>
        <div style='font-size: 1.1rem; font-weight: 700; color: #000;'>{user['full_name']}</div>
        <div style='font-size: 0.8rem; color: #0F21FD; font-weight: 600;'>{user['role'].upper()}</div>
    </div>
""", unsafe_allow_html=True)

render_lang_selector(sidebar=True)

if user['role'] == "client":
    refresh_user()
    user = st.session_state.user
    
    if user['status'] == "pending_approval":
        page_options = ["docs", "profile"]
        if 'client_nav_page' not in st.session_state or st.session_state.client_nav_page not in page_options:
            st.session_state.client_nav_page = "docs"
    else:
        page_options = ["list", "reports", "billing", "docs", "profile", "test"]
        if 'client_nav_page' not in st.session_state or st.session_state.client_nav_page not in page_options:
            st.session_state.client_nav_page = "list"
            
    try:
        nav_index = page_options.index(st.session_state.client_nav_page)
    except ValueError:
        nav_index = 0
        st.session_state.client_nav_page = page_options[0]
        
    pages_translation = {
        "list": L['nav_list'],
        "reports": L['nav_reports'],
        "billing": L['nav_billing'],
        "docs": L['nav_docs'],
        "profile": L['nav_profile'],
        "test": L['nav_test']
    }
    
    selected_page_key = st.sidebar.radio(
        L['title'], 
        page_options, 
        index=nav_index, 
        format_func=lambda x: pages_translation.get(x, x),
        key="client_radio_key"
    )
    
    if selected_page_key != st.session_state.client_nav_page:
        st.session_state.client_nav_page = selected_page_key
        st.session_state.show_form = False
        st.session_state.edit_id = None
        st.rerun()
elif user['role'] == "operator":
    if 'op_nav_index' not in st.session_state: st.session_state.op_nav_index = 0
    op_pages_list = [L['op_nav_approvals'], L['op_nav_health'], L['op_nav_clients']]
    op_pages_map = {
        L['op_nav_approvals']: "approvals",
        L['op_nav_health']: "health",
        L['op_nav_clients']: "clients"
    }
    page_label = st.sidebar.radio(L['op_nav_title'], op_pages_list, index=st.session_state.op_nav_index)
    page = op_pages_map[page_label]
    if st.session_state.op_nav_index != op_pages_list.index(page_label):
        st.session_state.op_nav_index = op_pages_list.index(page_label)
        st.rerun()
elif user['role'] == "admin":
    adm_pages = {
        L['adm_nav_logs']: "logs",
        L['adm_nav_config']: "config",
        L['adm_nav_users']: "users"
    }
    page_label = st.sidebar.radio(L['adm_nav_title'], list(adm_pages.keys()))
    page = adm_pages[page_label]

st.sidebar.write("---")
if st.sidebar.button(L['btn_logout'], use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user = None
    if "user_id" in st.query_params:
        try:
            del st.query_params["user_id"]
        except:
            pass
    st.rerun()

# --- MAIN CONTENT ---
if user['role'] == "client":
    page = st.session_state.client_nav_page
    if page == "list":
        if st.session_state.show_form:
            render_monitoring_form()
        else:
            st.header(L['header_list'])
            if st.button(L['btn_new_set'], type="primary"):
                st.session_state.show_form = True
                st.session_state.edit_id = None
                st.rerun()
            
            try:
                res = requests.get(f"{API_BASE_URL}/sets", params={"user_id": user['id']})
                if res.status_code == 200:
                    sets = res.json()
                    if not sets:
                        st.info(L['msg_no_sets'])
                    else:
                        for s in sets:
                            with st.container(border=True):
                                col_s1, col_s2, col_s3 = st.columns([3, 1, 1])
                                with col_s1:
                                    st.write(f"### {s['name']}")
                                    status_raw = s['status'].lower()
                                    status_map = {
                                        "stand_by": L.get("status_stand_by", "STAND-BY"),
                                        "awaiting_approval": L.get("status_awaiting", "AWAITING APPROVAL"),
                                        "approved": L.get("status_approved", "APPROVED"),
                                        "active": L.get("status_active", "ACTIVE"),
                                        "cancelled": "CANCELADO" if st.session_state.lang == "PT" else ("CANCELADO" if st.session_state.lang == "ES" else "CANCELLED")
                                    }
                                    status_display = status_map.get(status_raw, status_raw.upper())
                                    st.write(f"**Status:** {status_display}")
                                    st.write(f"**Tags:** {', '.join(s['search_terms'])}")
                                    if s.get('rules'):
                                        st.write("**Canais & Horários:**" if st.session_state.lang == "PT" else ("Channels & Times:" if st.session_state.lang == "EN" else "Canales & Horarios:"))
                                        for r in s['rules']:
                                            st.write(f"- {r['channel']}: {r['program_name']} ({r['start_time']}-{r['end_time']}) | *{format_days(r['days_of_week'], st.session_state.lang)}*")
                                with col_s2:
                                    if st.button(f"✏️ Edit", key=f"edit_{s['id']}"):
                                        st.session_state.edit_id = s['id']
                                        st.session_state.set_name = s['name']
                                        st.session_state.temp_terms = s['search_terms']
                                        st.session_state.temp_rules = s['rules']
                                        st.session_state.audience_enabled = s.get('audience_data_enabled', False)
                                        st.session_state.context_secs = s.get('clip_context_seconds', 15)
                                        st.session_state.show_form = True
                                        st.rerun()
                                with col_s3:
                                    if st.button(f"🗑️ Del", key=f"del_{s['id']}"):
                                        requests.delete(f"{API_BASE_URL}/sets/{s['id']}")
                                        st.rerun()
                                        
                                # Expander for occurrences (Visualizar Ocorrências)
                                exp_label = f"🔍 Ocorrências Identificadas ({s['name']})" if st.session_state.lang == "PT" else (f"🔍 Ocurrencias Identificadas ({s['name']})" if st.session_state.lang == "ES" else f"🔍 Identified Occurrences ({s['name']})")
                                with st.expander(exp_label, expanded=False):
                                    try:
                                        m_res = requests.get(f"{API_BASE_URL}/sets/{s['id']}/mentions")
                                        mentions = m_res.json() if m_res.status_code == 200 else []
                                    except Exception as e:
                                        mentions = []
                                        st.error(f"Erro de conexão ao buscar ocorrências: {e}")
                                    
                                    has_video = any(m.get('video_url') for m in mentions)
                                    
                                    if not has_video:
                                        col_m_act1, col_m_act2 = st.columns([2, 1])
                                        with col_m_act1:
                                            sim_lbl = "⚡ Simular Nova Ocorrência" if st.session_state.lang == "PT" else ("⚡ Simular Nueva Ocurrencia" if st.session_state.lang == "ES" else "⚡ Simulate New Occurrence")
                                        with col_m_act2:
                                            if st.button(sim_lbl, key=f"sim_btn_{s['id']}", use_container_width=True):
                                                import random
                                                tag = random.choice(s['search_terms']) if s['search_terms'] else "Kantar"
                                                phrases = [
                                                    f"E na entrevista de hoje, destacamos a importância da marca {tag} na transformação digital do setor.",
                                                    f"A {tag} lançou ontem uma nova campanha nacional que está gerando grande repercussão nas redes sociais.",
                                                    f"Análise de mercado indica crescimento expressivo para a {tag} neste primeiro semestre de 2026.",
                                                    f"Os analistas esportivos elogiaram a presença da marca {tag} nos painéis de patrocínio do estádio."
                                                ]
                                                transcription = random.choice(phrases)
                                                
                                                channels = ["ESPN", "GNT", "CNN", "HBO", "TNT"]
                                                channel = random.choice(channels)
                                                
                                                programs = {
                                                    "ESPN": "SportsCenter",
                                                    "GNT": "Saia Justa",
                                                    "CNN": "CNN Prime Time",
                                                    "HBO": "Cine News",
                                                    "TNT": "Match Day"
                                                }
                                                prog = programs.get(channel, "Jornal da Noite")
                                                
                                                payload = {
                                                    "channel": channel,
                                                    "program_name": prog,
                                                    "occurrence_time": datetime.utcnow().isoformat(),
                                                    "transcription": transcription,
                                                    "context": f"Trecho de áudio capturado e transcrito via Transcription Façade da Kantar para o termo '{tag}'.",
                                                    "video_url": "https://www.w3schools.com/html/mov_bbb.mp4",
                                                    "audience_share": random.randint(800, 2400),
                                                    "audience_rating": random.randint(200, 1200)
                                                }
                                                
                                                try:
                                                    post_res = requests.post(f"{API_BASE_URL}/sets/{s['id']}/mentions", json=payload)
                                                    if post_res.status_code == 200:
                                                        st.success("Ocorrência simulada com sucesso!")
                                                        st.rerun()
                                                    else:
                                                        st.error(f"Erro ao simular: {post_res.text}")
                                                except Exception as e:
                                                    st.error(f"Erro de conexão: {e}")
                                                
                                    if not mentions:
                                        st.info(L['msg_no_mentions'])
                                    else:
                                        st.write("#### Filtros e Métricas")
                                        col_fm1, col_m_stat1, col_m_stat2 = st.columns([2, 1, 1])
                                        
                                        with col_fm1:
                                            m_channels = sorted(list(set(m['channel'] for m in mentions)))
                                            sel_chan = st.selectbox(L['label_channel'], ["TODOS"] + m_channels, key=f"chan_filt_{s['id']}")
                                        
                                        filtered_mentions = mentions
                                        if sel_chan != "TODOS":
                                            filtered_mentions = [m for m in mentions if m['channel'] == sel_chan]
                                            
                                        rating_unit = "pontos" if st.session_state.lang == "PT" else ("puntos" if st.session_state.lang == "ES" else "points")
                                        with col_m_stat1:
                                            st.metric("Total Ocorrências", len(filtered_mentions))
                                        with col_m_stat2:
                                            avg_rating = sum(m.get('audience_rating', 0) for m in filtered_mentions) / len(filtered_mentions) / 100 if filtered_mentions else 0.0
                                            st.metric("Audiência Média (Rating)", f"{avg_rating:.1f} {rating_unit}")
                                            
                                        st.write("---")
                                        
                                        for i, m in enumerate(filtered_mentions):
                                            highlighted_text = m['transcription']
                                            for term in s['search_terms']:
                                                import re
                                                pattern = re.compile(re.escape(term), re.IGNORECASE)
                                                highlighted_text = pattern.sub(f'<mark style="background-color: #ffeb3b; color: black; font-weight: bold; padding: 2px 4px; border-radius: 4px;">{term}</mark>', highlighted_text)
                                                
                                            st.markdown(f"""
                                                <div style='background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #E8E8EE; margin-bottom: 15px;'>
                                                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                                                        <div>
                                                            <span style='background-color: #0F21FD; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;'>{m['channel']}</span>
                                                            <span style='font-size: 0.9rem; font-weight: bold; margin-left: 10px;'>{m.get('program_name', 'Programa')}</span>
                                                        </div>
                                                        <span style='font-size: 0.8rem; color: #64748b;'>⏰ {m['occurrence_time'][:19].replace('T', ' ')}</span>
                                                    </div>
                                                    <div style='font-size: 1.05rem; line-height: 1.4; color: #1e293b; margin-bottom: 15px;'>
                                                        {highlighted_text}
                                                    </div>
                                                </div>
                                            """, unsafe_allow_html=True)
                                            
                                            if s.get('audience_data_enabled') and (m.get('audience_rating') or m.get('audience_share')):
                                                col_aud1, col_aud2 = st.columns(2)
                                                with col_aud1:
                                                    st.caption(f"📊 **Audiência Rating:** {m.get('audience_rating', 0)/100:.2f} {rating_unit}")
                                                with col_aud2:
                                                    st.caption(f"📈 **Audiência Share:** {m.get('audience_share', 0)/100:.2f}%")
                                                    
                                            if m.get('video_url'):
                                                local_video_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "samplevideo.mp4"))
                                                if os.path.exists(local_video_path):
                                                    try:
                                                        with open(local_video_path, "rb") as video_file:
                                                            st.video(video_file.read())
                                                    except Exception as e:
                                                        st.video(m['video_url'])
                                                else:
                                                    st.video(m['video_url'])
                                                    
                                            st.caption(f"🔗 **Contexto:** {m.get('context', 'N/A')} (Margem: {s.get('clip_context_seconds', 15)}s)")
                                            st.write("---")
                else:
                    st.error("Error loading sets")
            except Exception as e:
                st.error(f"Connection error: {e}")
    
    elif page == "reports":
        st.header(L['header_reports'])
        
        try:
            sets_res = requests.get(f"{API_BASE_URL}/sets", params={"user_id": user['id']})
            all_sets = sets_res.json() if sets_res.status_code == 200 else []
        except Exception as e:
            all_sets = []
            st.error(f"Erro ao conectar ao servidor: {e}")
            
        active_sets = [s for s in all_sets if s['status'] in ["active", "approved"]]
        
        if not active_sets:
            st.info("Você precisa ter pelo menos um Conjunto de Monitoramento aprovado ou ativo para configurar relatórios automáticos.")
        else:
            set_options = {s['name']: s for s in active_sets}
            selected_set_name = st.selectbox(L['lbl_select_set'], list(set_options.keys()))
            selected_set = set_options[selected_set_name]
            
            # Fetch mentions for the set to calculate activity KPIs
            try:
                m_res = requests.get(f"{API_BASE_URL}/sets/{selected_set['id']}/mentions")
                mentions = m_res.json() if m_res.status_code == 200 else []
            except:
                mentions = []
                
            total_mentions = len(mentions)
            channels_list = [m['channel'] for m in mentions if m.get('channel')]
            programs_list = [m['program_name'] for m in mentions if m.get('program_name')]
            
            st.write("---")
            st.markdown("### 📈 Painel de Atividade do Monitoramento" if st.session_state.lang == "PT" else ("### 📈 Activity Dashboard" if st.session_state.lang == "EN" else "### 📈 Panel de Actividad"))
            col_k1, col_k2, col_k3 = st.columns(3)
            with col_k1:
                st.metric("Total de Ocorrências" if st.session_state.lang == "PT" else ("Total Occurrences" if st.session_state.lang == "EN" else "Total Ocurrencias"), total_mentions)
            with col_k2:
                top_channel = max(set(channels_list), key=channels_list.count) if channels_list else "N/A"
                st.metric("Emissora Líder" if st.session_state.lang == "PT" else ("Top Channel" if st.session_state.lang == "EN" else "Canal Líder"), top_channel)
            with col_k3:
                top_prog = max(set(programs_list), key=programs_list.count) if programs_list else "N/A"
                st.metric("Programa Líder" if st.session_state.lang == "PT" else ("Top Program" if st.session_state.lang == "EN" else "Programa Líder"), top_prog)
            
            st.write("---")
            
            current_config = None
            try:
                config_res = requests.get(f"{API_BASE_URL}/reports/config/{selected_set['id']}")
                if config_res.status_code == 200 and config_res.text:
                    current_config = config_res.json()
            except:
                pass
                
            st.subheader(L['lbl_report_config'])
            
            freq_keys = ["daily", "weekly", "monthly"]
            freq_labels = {
                "daily": L['freq_daily'],
                "weekly": L['freq_weekly'],
                "monthly": L['freq_monthly']
            }
            
            default_freq = current_config.get("frequency", "daily") if current_config else "daily"
            default_hour = current_config.get("hour", 8) if current_config else 8
            default_recipients = ", ".join(current_config.get("email_recipients", [])) if current_config else user['email']
            
            freq_selection = st.selectbox(
                L['label_frequency'], 
                freq_keys, 
                index=freq_keys.index(default_freq),
                format_func=lambda x: freq_labels.get(x, x)
            )
            
            hour_selection = st.number_input(L['label_hour'], min_value=0, max_value=23, value=default_hour)
            recipients_input = st.text_input(L['label_recipients'], value=default_recipients)
            
            if st.button(L['btn_save_config'], type="primary"):
                emails = [email.strip() for email in recipients_input.split(",") if email.strip()]
                payload = {
                    "monitoring_set_id": selected_set['id'],
                    "frequency": freq_selection,
                    "hour": hour_selection,
                    "email_recipients": emails
                }
                
                try:
                    save_res = requests.post(f"{API_BASE_URL}/reports/config", json=payload, params={"user_id": user['id']})
                    if save_res.status_code == 200:
                        st.success("Configuração de relatório salva com sucesso!")
                    else:
                        st.error(f"Erro ao salvar: {save_res.text}")
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")
                    
            st.write("---")
            
            st.subheader("Geração de Relatório Manual (On-Demand)" if st.session_state.lang == "PT" else ("Generate Report On-Demand" if st.session_state.lang == "EN" else "Generar Informe Manual (On-Demand)"))
            col_d1, col_d2, col_d3 = st.columns([2, 2, 2])
            with col_d1:
                start_date_input = st.date_input("Data de Início" if st.session_state.lang == "PT" else ("Start Date" if st.session_state.lang == "EN" else "Fecha de Inicio"), value=datetime.today() - timedelta(days=7))
            with col_d2:
                end_date_input = st.date_input("Data de Fim" if st.session_state.lang == "PT" else ("End Date" if st.session_state.lang == "EN" else "Fecha de Fin"), value=datetime.today())
            with col_d3:
                st.write("") # spacing
                st.write("") # spacing
                btn_lbl = "Gerar Relatório" if st.session_state.lang == "PT" else ("Generate Report" if st.session_state.lang == "EN" else "Generar Informe")
                if st.button(btn_lbl, key="manual_gen_report_btn", use_container_width=True):
                    try:
                        gen_res = requests.post(
                            f"{API_BASE_URL}/reports/generate", 
                            params={
                                "set_id": selected_set['id'], 
                                "user_id": user['id'],
                                "start_date": start_date_input.strftime("%Y-%m-%d"),
                                "end_date": end_date_input.strftime("%Y-%m-%d")
                            }
                        )
                        if gen_res.status_code == 200:
                            st.success("Relatório gerado com sucesso!" if st.session_state.lang == "PT" else ("Report generated successfully!" if st.session_state.lang == "EN" else "¡Informe generado con éxito!"))
                            st.rerun()
                        else:
                            st.error(f"Erro ao gerar: {gen_res.text}")
                    except Exception as e:
                        st.error(f"Erro de conexão: {e}")
                        
            st.write("---")
            st.subheader("Histórico de Relatórios" if st.session_state.lang == "PT" else ("Report History" if st.session_state.lang == "EN" else "Historial de Informes"))
            
            try:
                history_res = requests.get(f"{API_BASE_URL}/reports/history/{selected_set['id']}")
                reports = history_res.json() if history_res.status_code == 200 else []
                
                if not reports:
                    st.info("Nenhum relatório foi gerado automaticamente ou manualmente para este conjunto até o momento." if st.session_state.lang == "PT" else ("No reports have been generated for this set yet." if st.session_state.lang == "EN" else "No se han generado informes para este conjunto todavía."))
                else:
                    for r in reports:
                        # Format generated date
                        try:
                            gen_dt = datetime.strptime(r['generated_at'][:19], "%Y-%m-%dT%H:%M:%S")
                            gen_str = gen_dt.strftime("%d/%m/%Y %H:%M")
                        except:
                            gen_str = r['generated_at'][:19].replace('T', ' ')
                            
                        # Format period coverage
                        try:
                            ps_dt = datetime.strptime(r['period_start'][:10], "%Y-%m-%d")
                            ps_str = ps_dt.strftime("%d/%m/%Y")
                        except:
                            ps_str = r['period_start'][:10]
                            ps_dt = None
                            
                        try:
                            pe_dt = datetime.strptime(r['period_end'][:10], "%Y-%m-%d")
                            pe_str = pe_dt.strftime("%d/%m/%Y")
                        except:
                            pe_str = r['period_end'][:10]
                            pe_dt = None
                            
                        period_str = f"{ps_str} a {pe_str}" if st.session_state.lang == "PT" else (f"{ps_str} to {pe_str}" if st.session_state.lang == "EN" else f"{ps_str} a {pe_str}")
                        
                        # Count mentions in the report period
                        mentions_in_period = 0
                        if ps_dt and pe_dt:
                            for m in mentions:
                                try:
                                    occ_dt = datetime.strptime(m['occurrence_time'][:10], "%Y-%m-%d")
                                    if ps_dt.date() <= occ_dt.date() <= pe_dt.date():
                                        mentions_in_period += 1
                                except:
                                    pass
                        
                        file_name = r['file_url'].split('/')[-1] if '/' in r['file_url'] else r['file_url']
                        
                        with st.container(border=True):
                            col_c1, col_c2, col_c3 = st.columns([3, 2, 1.5])
                            with col_c1:
                                st.markdown(f"📄 **{file_name}**")
                                st.markdown(f"<span style='color: #64748b; font-size: 0.9rem;'>{'Gerado em' if st.session_state.lang == 'PT' else ('Generated on' if st.session_state.lang == 'EN' else 'Generado el')}: {gen_str}</span>", unsafe_allow_html=True)
                            with col_c2:
                                st.markdown(f"🗓️ **Período:** {period_str}")
                                st.markdown(f"📊 **{mentions_in_period}** ocorrências" if st.session_state.lang == "PT" else (f"📊 **{mentions_in_period}** occurrences" if st.session_state.lang == "EN" else f"📊 **{mentions_in_period}** ocurrencias"))
                            with col_c3:
                                btn_download_label = "⬇️ Download" if st.session_state.lang == "EN" else "⬇️ Baixar PDF" if st.session_state.lang == "PT" else "⬇️ Descargar"
                                st.markdown(f"""
                                    <a href='{r['file_url']}' target='_blank' style='
                                        display: inline-block;
                                        background-color: #64748b;
                                        color: white;
                                        padding: 8px 12px;
                                        text-align: center;
                                        text-decoration: none;
                                        font-size: 0.85rem;
                                        font-weight: 600;
                                        border-radius: 4px;
                                        margin-top: 5px;
                                        width: 100%;
                                    '>{btn_download_label}</a>
                                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erro ao carregar histórico de relatórios: {e}")

    elif page == "billing":
        st.header(L['nav_billing'])
        
        st.markdown(f"""
            <div style='background-color: #FAFAFA; padding: 20px; border-radius: 8px; border: 1px solid #E8E8EE; margin-bottom: 20px;'>
                <h4 style='margin:0 0 10px 0; color:#0F21FD;'>Resumo Financeiro da Conta</h4>
                <div style='display: flex; gap: 40px;'>
                    <div>
                        <div style='font-size:0.8rem; color:#64748b;'>LIMITE DE CRÉDITO DISPONÍVEL</div>
                        <div style='font-size:1.8rem; font-weight:700; color:#000;'>R$ {user.get('credit_limit', 0)/100:.2f}</div>
                    </div>
                    <div>
                        <div style='font-size:0.8rem; color:#64748b;'>STATUS DE ACESSO</div>
                        <div style='font-size:1.8rem; font-weight:700; color:{"green" if not user.get("is_blocked_access") else "red"};'>
                            {"ATIVO / LIBERADO" if not user.get("is_blocked_access") else "BLOQUEADO"}
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        st.subheader(L['header_billing'])
        
        try:
            invoices_res = requests.get(f"{API_BASE_URL}/invoices", params={"user_id": user['id']})
            invoices = invoices_res.json() if invoices_res.status_code == 200 else []
            
            if not invoices:
                st.info("Nenhuma fatura de serviço foi emitida para esta conta.")
            else:
                invoice_data = []
                status_translation = {
                    "pending": "Pendente",
                    "paid": "Pago",
                    "overdue": "Atrasado"
                }
                for inv in invoices:
                    due_date = inv['due_date']
                    amount_fmt = f"R$ {inv['amount']/100:.2f}"
                    status_fmt = status_translation.get(inv['status'], inv['status']).upper()
                    invoice_data.append({
                        "Período de Referência": inv['billing_period'],
                        L['th_amount']: amount_fmt,
                        L['th_due']: due_date,
                        L['th_status']: status_fmt,
                        "PDF / Boleto": inv.get('pdf_url', 'N/A')
                    })
                
                df_invoices = pd.DataFrame(invoice_data)
                st.dataframe(df_invoices, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao carregar histórico de faturamento: {e}")

    elif page == "profile":
        st.header(L['nav_profile'])
        st.write(f"**Name:** {user['full_name']}")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Role:** {user['role'].upper()}")

    elif page == "docs":
        st.header(L['header_docs'])
        
        status_map = {
            "missing": (L['lbl_docs_missing'], "orange"),
            "pending_review": (L['lbl_docs_sent'], "blue"),
            "verified": (L['lbl_docs_verified'], "green")
        }
        current_status = user.get("document_status", "missing")
        status_label, status_color = status_map.get(current_status, (L['lbl_docs_missing'], "orange"))
        
        st.markdown(f"#### Status Atual: <span style='color: {status_color}; font-weight: bold;'>{status_label}</span>", unsafe_allow_html=True)
        
        if user['status'] == "pending_approval":
            st.info("Sua conta está em processo de homologação. Faça o upload dos documentos obrigatórios abaixo e aguarde a validação do nosso Time Comercial.")
        
        st.write("---")
        
        uploaded_docs = user.get("documents", {}) or {}
        
        col_list1, col_list2 = st.columns(2)
        with col_list1:
            st.subheader(L['lbl_certidao'])
            if "certidao" in uploaded_docs:
                doc_info = uploaded_docs["certidao"]
                st.write(f"📄 **Arquivo:** `{doc_info.get('filename')}`")
                st.write(f"⏰ **Enviado em:** {doc_info.get('uploaded_at', '')[:19].replace('T', ' ')}")
            else:
                st.warning("Pendente de Envio")
                
        with col_list2:
            st.subheader(L['lbl_contrato'])
            if "contrato" in uploaded_docs:
                doc_info = uploaded_docs["contrato"]
                st.write(f"📄 **Arquivo:** `{doc_info.get('filename')}`")
                st.write(f"⏰ **Enviado em:** {doc_info.get('uploaded_at', '')[:19].replace('T', ' ')}")
            else:
                st.warning("Pendente de Envio")
                
        st.write("---")
        st.subheader(L['lbl_upload_docs'])
        
        certidao_file = st.file_uploader(L['lbl_certidao'], type=['pdf', 'docx', 'png', 'jpg'], key="certidao_uploader_widget")
        contrato_file = st.file_uploader(L['lbl_contrato'], type=['pdf', 'docx', 'png', 'jpg'], key="contrato_uploader_widget")
        
        if st.button(L['btn_send_docs'], type="primary", use_container_width=True):
            if not certidao_file and not contrato_file:
                st.warning("Selecione pelo menos um arquivo para enviar.")
            else:
                success = True
                with st.spinner("Enviando documentos..."):
                    if certidao_file:
                        files = {"file": (certidao_file.name, certidao_file.getvalue(), certidao_file.type)}
                        data = {"user_id": str(user['id']), "doc_type": "certidao"}
                        try:
                            res = requests.post(f"{API_BASE_URL}/user/upload-document", data=data, files=files)
                            if res.status_code != 200:
                                st.error(f"Erro ao enviar Certidão: {res.text}")
                                success = False
                        except Exception as e:
                            st.error(f"Erro de conexão: {e}")
                            success = False
                            
                    if contrato_file:
                        files = {"file": (contrato_file.name, contrato_file.getvalue(), contrato_file.type)}
                        data = {"user_id": str(user['id']), "doc_type": "contrato"}
                        try:
                            res = requests.post(f"{API_BASE_URL}/user/upload-document", data=data, files=files)
                            if res.status_code != 200:
                                st.error(f"Erro ao enviar Contrato Social: {res.text}")
                                success = False
                        except Exception as e:
                            st.error(f"Erro de conexão: {e}")
                            success = False
                
                if success:
                    st.success(L['msg_docs_success'])
                    refresh_user()
                    st.rerun()

elif user['role'] == "operator":
    if page == "approvals":
        st.header(L['op_nav_approvals'])
        tab1, tab2 = st.tabs([L['tab_new_clients'], L['tab_monitoring']])
        
        with tab1:
            try:
                res = requests.get(f"{API_BASE_URL}/operator/pending-clients")
                clients = res.json() if res.status_code == 200 else []
                if not clients:
                    st.info(L['msg_no_pending_clients'])
                else:
                    for c in clients:
                        with st.container(border=True):
                            st.write(f"**{c['company_name']}** ({c['full_name']})")
                            if st.button(f"Approve {c['company_name']}", key=f"app_c_{c['id']}"):
                                requests.patch(f"{API_BASE_URL}/operator/approve-client/{c['id']}")
                                st.rerun()
            except:
                st.error("Error loading pending clients")
                
        with tab2:
            try:
                res = requests.get(f"{API_BASE_URL}/operator/pending-sets")
                sets = res.json() if res.status_code == 200 else []
                if not sets:
                    st.info(L['msg_no_pending_sets'])
                else:
                    for s in sets:
                        with st.container(border=True):
                            st.write(f"### 📺 {s['name']}")
                            st.write(f"👤 **Cliente:** {s.get('client_name', 'N/A')} ({s.get('client_company', 'N/A')})")
                            st.write(f"⏱️ **Tempo Estimado:** {s.get('total_minutes', 0)} min")
                            st.write(f"💳 **Limite do Cliente:** R$ {s.get('client_credit_limit', 0)/100:.2f}")
                            if st.button(f"Approve Set {s['id']}", key=f"app_s_{s['id']}", type="primary"):
                                requests.patch(f"{API_BASE_URL}/sets/{s['id']}/status", params={"status": "active"})
                                st.rerun()
            except:
                st.error("Error loading pending sets")

    elif page == "health":
        st.header(L['op_nav_health'])
        try:
            res = requests.get(f"{API_BASE_URL}/operator/health")
            if res.status_code == 200:
                h = res.json()
                col_h1, col_h2, col_h3 = st.columns(3)
                with col_h1:
                    st.metric("Sets Ativos", h.get("active_sets", 0))
                with col_h2:
                    st.metric("Clientes Ativos", h.get("active_clients", 0))
                with col_h3:
                    st.metric("Erros de Execução", h.get("errors", 0))
                
                st.write("---")
                st.subheader("Processamentos em Execução")
                st.info(f"Dispatcher: ATIVO | Instâncias em execução: {h.get('running_now', 0)}")
            else:
                st.error("Erro ao carregar dados de saúde")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
            
    elif page == "clients":
        st.header(L['op_nav_clients'])
        try:
            res = requests.get(f"{API_BASE_URL}/operator/clients")
            if res.status_code == 200:
                clients = res.json()
                if not clients:
                    st.info("Nenhum cliente cadastrado.")
                else:
                    for c in clients:
                        with st.container(border=True):
                            col_c1, col_c2, col_c3 = st.columns([2, 1, 1])
                            with col_c1:
                                st.write(f"### {c['company_name']}")
                                st.write(f"👤 **Contato:** {c['full_name']} ({c['email']})")
                                st.write(f"💳 **Limite de Crédito:** R$ {c['credit_limit']/100:.2f}")
                                st.write(f"🔒 **Acesso Bloqueado:** {'Sim' if c['is_blocked_access'] else 'Não'}")
                                
                                doc_status_labels = {
                                    "missing": "❌ Sem Documentos",
                                    "pending_review": "📁 Pendente de Análise",
                                    "verified": "✅ Documentação Verificada"
                                }
                                st.write(f"📄 **Status de Documentos:** **{doc_status_labels.get(c.get('document_status'), 'Sem Documentos')}**")
                                
                                docs = c.get("documents", {}) or {}
                                if docs:
                                    st.write("**Arquivos Enviados:**")
                                    for doc_type, info in docs.items():
                                        label = "Certidão / CNPJ" if doc_type == "certidao" else "Contrato Social"
                                        st.write(f"- {label}: `{info.get('filename')}` (Enviado em: {info.get('uploaded_at', '')[:19].replace('T', ' ')})")
                            
                            with col_c2:
                                if c['is_blocked_access']:
                                    if st.button("Desbloquear", key=f"unblock_btn_{c['id']}"):
                                        requests.patch(f"{API_BASE_URL}/operator/user/{c['id']}/block", params={"block": False})
                                        st.rerun()
                                else:
                                    if st.button("Bloquear", key=f"block_btn_{c['id']}"):
                                        requests.patch(f"{API_BASE_URL}/operator/user/{c['id']}/block", params={"block": True})
                                        st.rerun()
                                        
                                if c['status'] == "pending_approval":
                                    if st.button("Aprovar Cliente", key=f"approve_client_btn_{c['id']}", type="primary"):
                                        requests.patch(f"{API_BASE_URL}/operator/approve-client/{c['id']}")
                                        st.rerun()
                                        
                            with col_c3:
                                new_limit = st.number_input("Novo Limite (R$)", value=float(c['credit_limit']/100), step=50.0, key=f"limit_input_{c['id']}")
                                if st.button("Ajustar Limite", key=f"limit_btn_{c['id']}"):
                                    requests.patch(f"{API_BASE_URL}/operator/user/{c['id']}/credit", params={"credit_limit": int(new_limit * 100)})
                                    st.rerun()
            else:
                st.error("Erro ao carregar clientes")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")

elif user['role'] == "admin":
    st.header("Admin Panel")
    st.info("Management modules under construction for v1.4.0")
