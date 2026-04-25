import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PJ STUDIO GOLD PRO", layout="wide")

# --- CONEXÃO SUPABASE (BLINDADA) ---
URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
KEY = "sb_publishable_qisG5bDBD-AxpBKW9LmBnA_p-_M671n"

try:
    supabase: Client = create_client(URL, KEY)
except Exception:
    st.error("Erro na conexão com o banco de dados.")
    st.stop()

# --- CSS PRETO E OURO PREMIUM (FOCO NA POSIÇÃO DO MENU) ---
st.markdown("""
    <style>
    /* Fundo Principal */
    .stApp { background-color: #0e1117; color: #FFFFFF; }
    
    /* Título Superior */
    h1 { 
        color: #D4AF37 !important; 
        text-align: center; 
        padding-bottom: 20px;
        font-weight: 800 !important;
    }

    /* FORÇAR MENU (TABS) NO TOPO */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 20px;
        border-bottom: 2px solid #D4AF37 !important;
        margin-bottom: 30px;
    }
    
    button[data-baseweb="tab"] {
        color: #FFFFFF !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        background-color: transparent !important;
    }
    
    button[aria-selected="true"] {
        color: #D4AF37 !important;
        border-bottom: 3px solid #D4AF37 !important;
    }

    /* Métricas (Abaixo do Menu) */
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 2.5rem !important; }
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

# --- FUNÇÕES DE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(212, 175, 55)
        self.cell(0, 15, 'PJ STUDIO GOLD PRO - ORÇAMENTO', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_projeto(dados, config, tipo="ORÇAMENTO"):
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"EMPRESA: {config.get('nome_empresa', 'PJ STUDIO')}", ln=True)
        pdf.cell(0, 10, f"WHATSAPP: {config.get('whatsapp', '---')}", ln=True)
        pdf.ln(10)
        pdf.cell(0, 10, f"CLIENTE: {dados.get('cliente', '---')}", ln=True)
        pdf.cell(0, 10, f"SERVIÇO: {dados.get('nome_projeto', '---')}", ln=True)
        v = float(dados.get('valor_total', 0))
        pdf.cell(0, 10, f"TOTAL: R$ {v:.2f}", ln=True)
        return pdf.output(dest='S').encode('latin-1')
    except: return None

# --- DADOS ---
def carregar_dados():
    try:
        proj = supabase.table("projetos").select("*").execute()
        conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
        return proj.data, conf.data[0] if conf.data else {}
    except: return [], {}

projetos, config = carregar_dados()

# Cálculo Métricas
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

# --- LAYOUT ---
st.title("⚜️ PJ STUDIO GOLD PRO")

# MENU NO TOPO (TABS)
tabs = st.tabs(["📋 GESTÃO", "➕ NOVO JOB", "⚙️ CONFIGURAÇÕES"])

with tabs[0]:
    # Métricas dentro da Gestão para manter o visual limpo
    c_m1, c_m2 = st.columns(2)
    c_m1.metric("💰 NO BOLSO", f"R$ {no_bolso:,.2f}")
    c_m2.metric("⏳ A RECEBER", f"R$ {a_receber:,.2f}")
    st.write("---")
    
    if not projetos:
        st.info("Nenhum projeto registrado.")
    for p in projetos:
        with st.expander(f"📌 {p.get('nome_projeto')} | {p.get('cliente')}"):
            c1, c2, c3 = st.columns(3)
            s_int = c1.selectbox("Integral", ["Pendente", "Recebido"], index=0 if p.get('status_integral')=='Pendente' else 1, key=f"i_{p['id']}")
            s_ent = c2.selectbox("Entrada", ["Pendente", "Recebido"], index=0 if p.get('status_entrada')=='Pendente' else 1, key=f"e_{p['id']}")
            s_fin = c3.selectbox("Final", ["Pendente", "Recebido"], index=0 if p.get('status_final')=='Pendente' else 1, key=f"f_{p['id']}")
            
            b1, b2, b3, b4 = st.columns(4)
            if b1.button("🔄 ATUALIZAR", key=f"u_{p['id']}"):
                supabase.table("projetos").update({"status_integral": s_int, "status_entrada": s_ent, "status_final": s_fin}).eq("id", p['id']).execute()
                st.rerun()
            pdf_orc = gerar_pdf_projeto(p, config, "ORÇAMENTO")
            if pdf_orc: b2.download_button("📄 PDF", pdf_orc, f"Orc_{p['id']}.pdf", key=f"p_{p['id']}")
            if b4.button("🗑️ EXCLUIR", key=f"d_{p['id']}"):
                supabase.table("projetos").delete().eq("id", p['id']).execute()
                st.rerun()

with tabs[1]:
    with st.form("job"):
        n = st.text_input("Projeto")
        c = st.text_input("Cliente")
        v = st.number_input("Valor", min_value=0.0)
        if st.form_submit_button("SALVAR"):
            supabase.table("projetos").insert({"nome_projeto": n, "cliente": c, "valor_total": v, "status_integral": "Pendente", "status_entrada": "Pendente", "status_final": "Pendente"}).execute()
            st.rerun()

with tabs[2]:
    with st.form("cfg"):
        nome_e = st.text_input("Empresa", value=config.get('nome_empresa', ''))
        zap_e = st.text_input("WhatsApp", value=config.get('whatsapp', ''))
        if st.form_submit_button("SALVAR"):
            supabase.table("configuracoes").update({"nome_empresa": nome_e, "whatsapp": zap_e}).eq("id", 1).execute()
            st.rerun()
