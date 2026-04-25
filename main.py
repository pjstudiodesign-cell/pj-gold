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

# --- CSS PRETO E OURO PREMIUM (FOCO NA IDENTIDADE E SIDEBAR) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #FFFFFF; }
    
    /* Sidebar Blindada */
    [data-testid="stSidebar"] {
        background-color: #121212 !important;
        border-right: 2px solid #D4AF37 !important;
    }

    /* Navegação em Ouro */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {
        color: #D4AF37 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }
    
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 800 !important; }
    
    /* Cards de Métricas */
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 2.8rem !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    div[data-testid="stMetric"] { 
        background-color: #1c1c1c; 
        padding: 25px; 
        border-radius: 15px; 
        border: 2px solid #D4AF37; 
    }
    
    /* Botões Ouro */
    .stButton>button { 
        background-color: #D4AF37 !important; 
        color: black !important; 
        font-weight: bold !important; 
        border-radius: 10px !important;
        height: 45px;
        width: 100%;
    }

    /* Inputs e Forms */
    input, textarea, div[data-baseweb="select"] { 
        background-color: #1c1c1c !important; 
        color: white !important; 
        border: 1px solid #444 !important; 
    }
    label { color: #D4AF37 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS E PDF ---
def carregar_dados():
    try:
        proj = supabase.table("projetos").select("*").execute()
        conf = supabase.table("configuracoes").select("*").eq("id", 1).execute()
        return proj.data, conf.data[0] if conf.data else {}
    except: return [], {}

def gerar_pdf_completo(dados, config, tipo="ORÇAMENTO"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(212, 175, 55)
        pdf.cell(0, 15, f'PJ STUDIO GOLD - {tipo}', 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "DADOS DO CLIENTE", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 8, f"Cliente: {dados.get('cliente')}", ln=True)
        pdf.cell(0, 8, f"CPF/CNPJ: {dados.get('cpf_cnpj', '---')}", ln=True)
        pdf.cell(0, 8, f"WhatsApp: {dados.get('whatsapp_cliente', '---')}", ln=True)
        pdf.cell(0, 8, f"E-mail: {dados.get('email_cliente', '---')}", ln=True)
        pdf.cell(0, 8, f"Endereço: {dados.get('endereco', '---')}", ln=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "DETALHES DO SERVIÇO", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 8, f"Projeto: {dados.get('nome_projeto')}", ln=True)
        pdf.cell(0, 8, f"Valor Integral: R$ {float(dados.get('valor_total', 0)):.2f}", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, "Descrição Geral:", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 8, dados.get('descricao', '---'))
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, "Exigências Específicas do Cliente:", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 8, dados.get('exigencias', '---'))
        
        return pdf.output(dest='S').encode('latin-1')
    except: return None

# --- PROCESSAMENTO ---
projetos, config = carregar_dados()
no_bolso = sum([float(p.get('valor_total', 0)) for p in projetos if p.get('status_integral') == 'Recebido'])
# Lógica simplificada para o exemplo, mantendo sua estrutura de cálculos anterior se necessário

# --- SIDEBAR NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("## ⚜️ PJ STUDIO")
    st.write("---")
    menu = st.radio("NAVEGAÇÃO", ["PAINEL", "NOVO ORÇAMENTO", "GESTAO DE PROJETOS", "CONFIGURAÇOES"], label_visibility="collapsed")

# --- INTERFACE ---
if menu == "PAINEL":
    st.title("⚜️ PAINEL DE CONTROLE")
    c1, c2 = st.columns(2)
    c1.metric("💰 DINHEIRO NO BOLSO", f"R$ {no_bolso:,.2f}")
    c2.metric("⏳ CONTAS A RECEBER", "R$ 0.00")

elif menu == "NOVO ORÇAMENTO":
    st.title("➕ NOVO ORÇAMENTO COMPLETO")
    with st.form("orcamento_form", clear_on_submit=True):
        st.subheader("Dados do Cliente")
        c_nome = st.text_input("Nome Completo / Razão Social")
        col1, col2 = st.columns(2)
        c_doc = col1.text_input("CPF ou CNPJ")
        c_zap = col2.text_input("WhatsApp de Contato")
        c_mail = st.text_input("E-mail do Cliente")
        c_end = st.text_area("Endereço Completo")
        
        st.write("---")
        st.subheader("Detalhes do Orçamento")
        p_nome = st.text_input("Título do Projeto (Ex: Identidade Visual Premium)")
        p_valor = st.number_input("Valor Total do Serviço (R$)", min_value=0.0, format="%.2f")
        p_desc = st.text_area("Descrição Geral do Serviço")
        p_exig = st.text_area("Exigências e Detalhes Solicitados pelo Cliente")
        
        if st.form_submit_button("SALVAR ORÇAMENTO"):
            if c_nome and p_nome:
                supabase.table("projetos").insert({
                    "cliente": c_nome, "cpf_cnpj": c_doc, "whatsapp_cliente": c_zap,
                    "email_cliente": c_mail, "endereco": c_end, "nome_projeto": p_nome,
                    "valor_total": p_valor, "descricao": p_desc, "exigencias": p_exig,
                    "status_integral": "Pendente"
                }).execute()
                st.success("Orçamento salvo com sucesso! Vá para Gestão para gerar o PDF.")
                st.rerun()

elif menu == "GESTAO DE PROJETOS":
    st.title("📋 GESTÃO DE PROJETOS")
    for p in projetos:
        with st.expander(f"📌 {p.get('nome_projeto')} | {p.get('cliente')}"):
            st.write(f"**WhatsApp:** {p.get('whatsapp_cliente')} | **Valor:** R$ {p.get('valor_total')}")
            
            col_b1, col_b2 = st.columns(2)
            pdf_data = gerar_pdf_completo(p, config)
            if pdf_data:
                col_b1.download_button("📄 GERAR PDF ORÇAMENTO", pdf_data, f"Orcamento_{p.get('id')}.pdf", key=f"pdf_{p.get('id')}")
            
            if col_b2.button("🗑️ EXCLUIR", key=f"del_{p.get('id')}"):
                supabase.table("projetos").delete().eq("id", p.get('id')).execute()
                st.rerun()

elif menu == "CONFIGURAÇOES":
    st.title("⚙️ CONFIGURAÇÕES DA EMPRESA")
    with st.form("cfg"):
        n_emp = st.text_input("Nome da Empresa", value=config.get('nome_empresa', ''))
        w_emp = st.text_input("WhatsApp Profissional", value=config.get('whatsapp', ''))
        e_emp = st.text_input("E-mail Profissional", value=config.get('email', ''))
        if st.form_submit_button("SALVAR DADOS"):
            supabase.table("configuracoes").update({"nome_empresa": n_emp, "whatsapp": w_emp, "email": e_emp}).eq("id", 1).execute()
            st.rerun()
