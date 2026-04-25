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

# --- CSS PRETO E OURO PREMIUM (IDENTIDADE VISUAL PRESERVADA) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #FFFFFF; }
    [data-testid="stSidebar"] {
        background-color: #121212 !important;
        border-right: 2px solid #D4AF37 !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {
        color: #D4AF37 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }
    h1, h2, h3 { color: #D4AF37 !important; font-weight: 800 !important; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 2.8rem !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    div[data-testid="stMetric"] { 
        background-color: #1c1c1c; 
        padding: 25px; 
        border-radius: 15px; 
        border: 2px solid #D4AF37; 
    }
    .stButton>button { 
        background-color: #D4AF37 !important; 
        color: black !important; 
        font-weight: bold !important; 
        border-radius: 10px !important;
        height: 45px;
        width: 100%;
    }
    input, textarea, div[data-baseweb="select"] { 
        background-color: #1c1c1c !important; 
        color: white !important; 
        border: 1px solid #444 !important; 
    }
    label { color: #D4AF37 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE CARREGAMENTO E PDF ---
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
        pdf.cell(0, 15, f'{config.get("nome_empresa", "PJ STUDIO").upper()} - {tipo}', 0, 1, 'C')
        pdf.ln(5)
        pdf.set_font("Arial", size=9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"CNPJ: {config.get('cpf_cnpj', '---')} | Contato: {config.get('whatsapp', '---')}", ln=True, align='C')
        pdf.cell(0, 5, f"Endereço: {config.get('endereco', '---')}", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "DADOS DO CLIENTE", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 8, f"Cliente: {dados.get('cliente')}", ln=True)
        pdf.cell(0, 8, f"CPF/CNPJ: {dados.get('cpf_cnpj', '---')}", ln=True)
        pdf.cell(0, 8, f"WhatsApp: {dados.get('whatsapp_cliente', '---')}", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "DETALHES DO SERVIÇO", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 8, f"Projeto: {dados.get('nome_projeto')}", ln=True)
        pdf.cell(0, 8, f"Valor: R$ {float(dados.get('valor_total', 0)):.2f}", ln=True)
        pdf.cell(0, 8, f"PRAZO DE ENTREGA: {dados.get('prazo', '---')}", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, "Descrição:", ln=True)
        pdf.multi_cell(0, 7, dados.get('descricao', '---'))
        return pdf.output(dest='S').encode('latin-1')
    except: return None

# --- PROCESSAMENTO ---
projetos, config = carregar_dados()
no_bolso = sum([float(p.get('valor_total', 0)) for p in projetos if p.get('status_integral') == 'Recebido'])

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
    st.title("➕ NOVO ORÇAMENTO")
    # Blindagem: Removi o clear_on_submit para evitar perda de dados acidental
    with st.form("orcamento_form"):
        st.subheader("Dados do Cliente")
        c_nome = st.text_input("Nome/Razão Social")
        col1, col2 = st.columns(2)
        c_doc = col1.text_input("CPF ou CNPJ")
        c_zap = col2.text_input("WhatsApp")
        c_end = st.text_area("Endereço do Cliente")
        st.write("---")
        st.subheader("Serviço e Prazo")
        p_nome = st.text_input("Nome do Projeto")
        col3, col4 = st.columns(2)
        p_valor = col3.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
        p_prazo = col4.text_input("Prazo de Entrega")
        p_desc = st.text_area("Descrição do Serviço")
        p_exig = st.text_area("Exigências Específicas")
        
        # O botão agora exige preenchimento mínimo para evitar salvar vazio por erro de tecla
        submit = st.form_submit_button("SALVAR ORÇAMENTO")
        if submit:
            if not c_nome or not p_nome:
                st.warning("⚠️ Preencha pelo menos o Nome do Cliente e do Projeto antes de salvar.")
            else:
                supabase.table("projetos").insert({
                    "cliente": c_nome, "cpf_cnpj": c_doc, "whatsapp_cliente": c_zap,
                    "endereco": c_end, "nome_projeto": p_nome, "valor_total": p_valor, 
                    "prazo": p_prazo, "descricao": p_desc, "exigencias": p_exig,
                    "status_integral": "Pendente"
                }).execute()
                st.success("✅ Orçamento blindado e salvo na nuvem!")
                st.balloons()

elif menu == "GESTAO DE PROJETOS":
    st.title("📋 GESTÃO E EDIÇÃO")
    if not projetos:
        st.info("Nenhum orçamento cadastrado.")
    for p in projetos:
        with st.expander(f"📌 {p.get('nome_projeto')} | {p.get('cliente')}"):
            with st.form(f"edit_{p['id']}"):
                col_e1, col_e2 = st.columns(2)
                e_valor = col_e1.number_input("Valor", value=float(p.get('valor_total', 0)), key=f"val_{p['id']}")
                e_prazo = col_e2.text_input("Prazo", value=p.get('prazo', ''), key=f"prz_{p['id']}")
                e_desc = st.text_area("Descrição", value=p.get('descricao', ''), key=f"des_{p['id']}")
                
                if st.form_submit_button("💾 SALVAR ALTERAÇÕES"):
                    supabase.table("projetos").update({"valor_total": e_valor, "prazo": e_prazo, "descricao": e_desc}).eq("id", p['id']).execute()
                    st.success("Alteração salva!")
                    st.rerun()
            
            pdf_data = gerar_pdf_completo(p, config)
            if pdf_data:
                st.download_button("📄 GERAR PDF", pdf_data, f"Orc_{p['id']}.pdf", key=f"pdf_{p['id']}")
            
            if st.button("🗑️ EXCLUIR", key=f"del_{p['id']}"):
                supabase.table("projetos").delete().eq("id", p['id']).execute()
                st.rerun()

elif menu == "CONFIGURAÇOES":
    st.title("⚙️ DADOS DA MINHA EMPRESA")
    with st.form("cfg_completa"):
        n_emp = st.text_input("Nome da Empresa", value=config.get('nome_empresa', ''))
        c_emp = st.text_input("CPF ou CNPJ", value=config.get('cpf_cnpj', ''))
        w_emp = st.text_input("WhatsApp", value=config.get('whatsapp', ''))
        e_emp = st.text_input("E-mail", value=config.get('email', ''))
        end_emp = st.text_area("Endereço Completo", value=config.get('endereco', ''))
        
        if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
            supabase.table("configuracoes").update({
                "nome_empresa": n_emp, "cpf_cnpj": c_emp, "whatsapp": w_emp, "email": e_emp, "endereco": end_emp
            }).eq("id", 1).execute()
            st.success("Dados atualizados!")
            st.rerun()
