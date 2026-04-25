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

# --- CSS PRETO E OURO PREMIUM (ORDEM: SIDEBAR OURO + ESTRUTURA BLINDADA) ---
st.markdown("""
    <style>
    /* Fundo Total */
    .stApp { background-color: #0e1117; color: #FFFFFF; }
    
    /* Sidebar Blindada com borda Ouro */
    [data-testid="stSidebar"] {
        background-color: #121212 !important;
        border-right: 2px solid #D4AF37 !important;
    }

    /* COR OURO NAS LETRAS DO MENU (LINKS LATERAIS) */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #D4AF37 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        cursor: pointer;
    }
    
    /* Títulos do Sistema */
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 800 !important; }
    
    /* Métricas (Painel de Controle) */
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 2.8rem !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    div[data-testid="stMetric"] { 
        background-color: #1c1c1c; 
        padding: 25px; 
        border-radius: 15px; 
        border: 2px solid #D4AF37; 
        box-shadow: 0px 4px 20px rgba(212, 175, 55, 0.15);
    }
    
    /* Botões Ouro Profissional */
    .stButton>button { 
        background-color: #D4AF37 !important; 
        color: black !important; 
        font-weight: bold !important; 
        border-radius: 10px !important; 
        border: none !important;
        height: 45px;
    }
    .stButton>button:hover { background-color: #F5D76E !important; transform: scale(1.02); }
    
    /* Gestão de Projetos (Expanders) */
    div[data-testid="stExpander"] { 
        border: 1px solid #D4AF37 !important; 
        background-color: #121212 !important; 
        border-radius: 10px !important;
        margin-bottom: 15px;
    }

    /* Inputs e Seleções */
    input, textarea, div[data-baseweb="select"] { 
        background-color: #1c1c1c !important; 
        color: white !important; 
        border: 1px solid #444 !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE CARREGAMENTO E DOCUMENTOS ---
def carregar_dados():
    try:
        proj = supabase.table("projetos").select("*").execute()
        conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
        return proj.data, conf.data[0] if conf.data else {}
    except: return [], {}

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(212, 175, 55)
        self.cell(0, 15, 'PJ STUDIO GOLD PRO', 0, 1, 'C')
        self.ln(5)

def gerar_pdf(dados, config, tipo="ORÇAMENTO"):
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"EMPRESA: {config.get('nome_empresa', 'PJ STUDIO DESIGN')}", ln=True)
        pdf.cell(0, 10, f"CONTATO: {config.get('whatsapp', '---')} | {config.get('email', '---')}", ln=True)
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"DOCUMENTO: {tipo}", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"CLIENTE: {dados.get('cliente', '---')}", ln=True)
        pdf.cell(0, 10, f"PROJETO: {dados.get('nome_projeto', '---')}", ln=True)
        pdf.cell(0, 10, f"VALOR: R$ {float(dados.get('valor_total', 0)):.2f}", ln=True)
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"DESCRIÇÃO: {dados.get('descricao', '---')}")
        return pdf.output(dest='S').encode('latin-1')
    except: return None

# --- PROCESSAMENTO ---
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

# --- SIDEBAR (MENU LATERAL OURO) ---
with st.sidebar:
    st.markdown("## ⚜️ PJ STUDIO")
    st.write("---")
    menu = st.radio(
        "NAVEGAÇÃO",
        ["PAINEL", "NOVO ORÇAMENTO", "GESTAO DE PROJETOS", "CONFIGURAÇOES"],
        label_visibility="collapsed"
    )

# --- CONTEÚDO PRINCIPAL (BLINDADO) ---

if menu == "PAINEL":
    st.title("⚜️ PAINEL DE CONTROLE")
    col1, col2 = st.columns(2)
    col1.metric("💰 DINHEIRO NO BOLSO", f"R$ {no_bolso:,.2f}")
    col2.metric("⏳ CONTAS A RECEBER", f"R$ {a_receber:,.2f}")

elif menu == "NOVO ORÇAMENTO":
    st.title("➕ NOVO ORÇAMENTO")
    with st.form("job_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        n_p = col_a.text_input("Nome do Projeto")
        c_p = col_b.text_input("Nome do Cliente")
        d_p = st.text_area("Descrição do Serviço")
        v_p = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
        if st.form_submit_button("SALVAR E BLINDAR PROJETO"):
            if n_p and c_p:
                supabase.table("projetos").insert({
                    "nome_projeto": n_p, "cliente": c_p, "descricao": d_p, "valor_total": v_p,
                    "status_integral": "Pendente", "status_entrada": "Pendente", "status_final": "Pendente"
                }).execute()
                st.success("Projeto registrado no sistema!")
                st.rerun()

elif menu == "GESTAO DE PROJETOS":
    st.title("📋 GESTÃO DE PROJETOS")
    if not projetos:
        st.info("Nenhum projeto registrado.")
    for p in projetos:
        with st.expander(f"📌 {p.get('nome_projeto')} | CLIENTE: {p.get('cliente')}"):
            c1, c2, c3 = st.columns(3)
            s_int = c1.selectbox("Integral", ["Pendente", "Recebido"], index=0 if p.get('status_integral')=='Pendente' else 1, key=f"i_{p['id']}")
            s_ent = c2.selectbox("Entrada", ["Pendente", "Recebido"], index=0 if p.get('status_entrada')=='Pendente' else 1, key=f"e_{p['id']}")
            s_fin = c3.selectbox("Final", ["Pendente", "Recebido"], index=0 if p.get('status_final')=='Pendente' else 1, key=f"f_{p['id']}")
            
            b1, b2, b3, b4 = st.columns(4)
            if b1.button("🔄 ATUALIZAR", key=f"u_{p['id']}"):
                supabase.table("projetos").update({"status_integral": s_int, "status_entrada": s_ent, "status_final": s_fin}).eq("id", p['id']).execute()
                st.rerun()
            
            pdf_orc = gerar_pdf(p, config, "ORÇAMENTO")
            if pdf_orc: b2.download_button("📄 PDF ORC", pdf_orc, f"Orc_{p['id']}.pdf", key=f"po_{p['id']}")
            
            pdf_rec = gerar_pdf(p, config, "RECIBO")
            if pdf_rec: b3.download_button("🧾 RECIBO", pdf_rec, f"Rec_{p['id']}.pdf", key=f"pr_{p['id']}")
            
            if b4.button("🗑️ EXCLUIR", key=f"d_{p['id']}"):
                supabase.table("projetos").delete().eq("id", p['id']).execute()
                st.rerun()

elif menu == "CONFIGURAÇOES":
    st.title("⚙️ CONFIGURAÇÕES")
    with st.form("cfg_form"):
        n_e = st.text_input("Empresa", value=config.get('nome_empresa', ''))
        z_e = st.text_input("WhatsApp", value=config.get('whatsapp', ''))
        m_e = st.text_input("E-mail", value=config.get('email', ''))
        if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
            supabase.table("configuracoes").update({"nome_empresa": n_e, "whatsapp": z_e, "email": m_e}).eq("id", 1).execute()
            st.success("Configurações atualizadas!")
            st.rerun()
