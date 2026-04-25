import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PJ STUDIO GOLD PRO", layout="wide")

# --- CONEXÃO SUPABASE (ESTRUTURA BLINDADA) ---
URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY = "sb_publishable_qisG5bDBD-AxpBKW9LmBnA_p-_M671n"

try:
    supabase: Client = create_client(URL, KEY)
except Exception:
    st.error("Erro na conexão com o banco de dados.")
    st.stop()

# --- CSS PRETO E OURO PREMIUM (FOCO EXTREMO NAS LETRAS DO MENU) ---
st.markdown("""
    <style>
    /* Fundo Total */
    .stApp { background-color: #0e1117; color: #FFFFFF; }
    
    /* Sidebar Blindada */
    [data-testid="stSidebar"] {
        background-color: #121212 !important;
        border-right: 2px solid #D4AF37 !important;
    }

    /* CORREÇÃO CIRÚRGICA: LETRAS DO MENU EM OURO */
    /* Este seletor ataca diretamente o texto dos Radio Buttons na Sidebar */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {
        color: #D4AF37 !important;
        font-weight: bold !important;
        font-size: 1.2rem !important;
    }
    
    /* Cor do círculo de seleção (Ouro) */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] div[data-testid="stMarkdownContainer"] {
        color: #D4AF37 !important;
    }
    
    /* Títulos e Identidade */
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 800 !important; }
    
    /* Métricas (Cards Ouro) */
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 2.5rem !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    div[data-testid="stMetric"] { 
        background-color: #1c1c1c; 
        padding: 20px; 
        border-radius: 12px; 
        border: 2px solid #D4AF37; 
    }
    
    /* Botões Ouro */
    .stButton>button { 
        background-color: #D4AF37 !important; 
        color: black !important; 
        font-weight: bold !important; 
        border-radius: 8px !important;
    }

    /* Expanders */
    div[data-testid="stExpander"] { 
        border: 1px solid #D4AF37 !important; 
        background-color: #121212 !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE CARREGAMENTO E PDF (BLINDADAS) ---
def carregar_dados():
    try:
        proj = supabase.table("projetos").select("*").execute()
        conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
        return proj.data, conf.data[0] if conf.data else {}
    except: return [], {}

def gerar_pdf_projeto(dados, config, tipo="ORÇAMENTO"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(212, 175, 55)
        pdf.cell(0, 15, f'PJ STUDIO GOLD - {tipo}', 0, 1, 'C')
        pdf.ln(10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Empresa: {config.get('nome_empresa', 'PJ Studio')}", ln=True)
        pdf.cell(0, 10, f"WhatsApp: {config.get('whatsapp', '---')}", ln=True)
        pdf.ln(5)
        pdf.cell(0, 10, f"Cliente: {dados.get('cliente', '---')}", ln=True)
        pdf.cell(0, 10, f"Serviço: {dados.get('nome_projeto', '---')}", ln=True)
        v = float(dados.get('valor_total', 0))
        pdf.cell(0, 10, f"Valor Total: R$ {v:.2f}", ln=True)
        return pdf.output(dest='S').encode('latin-1')
    except: return None

# --- PROCESSAMENTO DE DADOS ---
projetos, config = carregar_dados()

no_bolso = 0
a_receber = 0
for p in projetos:
    try:
        v = float(p.get('valor_total', 0))
        if p.get('status_integral') == 'Recebido': no_bolso += v
        else:
            if p.get('status_entrada') == 'Recebido': no_bolso += (v * 0.5)
            else: a_receber += (v * 0.5)
            if p.get('status_final') == 'Recebido': no_bolso += (v * 0.5)
            else: a_receber += (v * 0.5)
    except: continue

# --- SIDEBAR (NAVEGAÇÃO COM CORREÇÃO DE COR) ---
with st.sidebar:
    st.markdown("### ⚜️ PJ STUDIO")
    st.write("---")
    # Menu lateral com rádio botões
    menu = st.radio(
        "MENU DE NAVEGAÇÃO",
        ["PAINEL", "NOVO ORÇAMENTO", "GESTAO DE PROJETOS", "CONFIGURAÇOES"],
        label_visibility="collapsed"
    )

# --- CONTEÚDO PRINCIPAL (ESTRUTURA MANTIDA) ---

if menu == "PAINEL":
    st.title("⚜️ PAINEL DE CONTROLE")
    col1, col2 = st.columns(2)
    col1.metric("💰 DINHEIRO NO BOLSO", f"R$ {no_bolso:,.2f}")
    col2.metric("⏳ CONTAS A RECEBER", f"R$ {a_receber:,.2f}")

elif menu == "NOVO ORÇAMENTO":
    st.title("➕ NOVO ORÇAMENTO")
    with st.form("job_form"):
        n_p = st.text_input("Nome do Projeto")
        c_p = st.text_input("Nome do Cliente")
        d_p = st.text_area("Descrição")
        v_p = st.number_input("Valor Total", min_value=0.0)
        if st.form_submit_button("SALVAR PROJETO"):
            if n_p and c_p:
                supabase.table("projetos").insert({"nome_projeto": n_p, "cliente": c_p, "descricao": d_p, "valor_total": v_p, "status_integral": "Pendente", "status_entrada": "Pendente", "status_final": "Pendente"}).execute()
                st.success("Salvo com sucesso!")
                st.rerun()

elif menu == "GESTAO DE PROJETOS":
    st.title("📋 GESTÃO DE PROJETOS")
    if not projetos:
        st.info("Nenhum projeto registrado.")
    for p in projetos:
        with st.expander(f"📌 {p.get('nome_projeto')} | {p.get('cliente')}"):
            c1, c2, c3 = st.columns(3)
            s_int = c1.selectbox("Integral", ["Pendente", "Recebido"], index=0 if p.get('status_integral')=='Pendente' else 1, key=f"int_{p['id']}")
            s_ent = c2.selectbox("Entrada (50%)", ["Pendente", "Recebido"], index=0 if p.get('status_entrada')=='Pendente' else 1, key=f"ent_{p['id']}")
            s_fin = c3.selectbox("Final (50%)", ["Pendente", "Recebido"], index=0 if p.get('status_final')=='Pendente' else 1, key=f"fin_{p['id']}")
            
            b1, b2, b3 = st.columns(3)
            if b1.button("🔄 ATUALIZAR", key=f"u_{p['id']}"):
                supabase.table("projetos").update({"status_integral": s_int, "status_entrada": s_ent, "status_final": s_fin}).eq("id", p['id']).execute()
                st.rerun()
            
            pdf_orc = gerar_pdf_projeto(p, config, "ORÇAMENTO")
            if pdf_orc: b2.download_button("📄 PDF", pdf_orc, f"Orc_{p['id']}.pdf", key=f"p_{p['id']}")
            
            if b3.button("🗑️ EXCLUIR", key=f"d_{p['id']}"):
                supabase.table("projetos").delete().eq("id", p['id']).execute()
                st.rerun()

elif menu == "CONFIGURAÇOES":
    st.title("⚙️ CONFIGURAÇÕES")
    with st.form("config_form"):
        n_e = st.text_input("Nome da Empresa", value=config.get('nome_empresa', ''))
        z_e = st.text_input("WhatsApp", value=config.get('whatsapp', ''))
        if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
            supabase.table("configuracoes").update({"nome_empresa": n_e, "whatsapp": z_e}).eq("id", 1).execute()
            st.success("Configurações atualizadas!")
            st.rerun()
